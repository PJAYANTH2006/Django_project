from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from internships.models import InternshipPosting, PostingRequiredSkill, Application, PlacementRecord
from internships.forms import InternshipPostingForm, AddPostingSkillForm, ApplicationStatusUpdateForm
from accounts.models import CompanyProfile, StudentProfile
from skills.models import Skill
from skills.automation import calculate_skill_gap, check_placement_eligibility
from notifications.models import create_notification


def internship_list_view(request):
    query = request.GET.get('q', '').strip()
    posting_type = request.GET.get('type', '')
    
    postings_qs = InternshipPosting.objects.filter(is_active=True).select_related('company').prefetch_related('required_skills__skill')

    if query:
        postings_qs = postings_qs.filter(
            Q(title__icontains=query) |
            Q(company__company_name__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query) |
            Q(required_skills__skill__name__icontains=query)
        ).distinct()

    if posting_type:
        postings_qs = postings_qs.filter(posting_type=posting_type)

    postings_with_analysis = []
    student_profile = None
    if request.user.is_authenticated and request.user.is_student:
        student_profile = getattr(request.user, 'student_profile', None)

    for posting in postings_qs:
        gap_info = None
        eligibility = None
        if student_profile:
            gap_info = calculate_skill_gap(student_profile, posting)
            eligibility = check_placement_eligibility(student_profile, posting, gap_info['match_percentage'])

        postings_with_analysis.append({
            'posting': posting,
            'gap_info': gap_info,
            'eligibility': eligibility,
        })

    # If student, sort by match percentage
    if student_profile:
        postings_with_analysis.sort(key=lambda x: (x['gap_info']['match_percentage'] if x['gap_info'] else 0), reverse=True)

    context = {
        'postings_with_analysis': postings_with_analysis,
        'query': query,
        'posting_type': posting_type,
    }
    return render(request, 'internships/list.html', context)


def internship_detail_view(request, pk):
    posting = get_object_or_404(InternshipPosting.objects.select_related('company'), pk=pk)
    required_skills = posting.required_skills.select_related('skill').all()
    
    gap_info = None
    eligibility = None
    existing_application = None

    if request.user.is_authenticated and request.user.is_student:
        student_profile = request.user.student_profile
        gap_info = calculate_skill_gap(student_profile, posting)
        eligibility = check_placement_eligibility(student_profile, posting, gap_info['match_percentage'])
        existing_application = Application.objects.filter(posting=posting, student=student_profile).first()

    context = {
        'posting': posting,
        'required_skills': required_skills,
        'gap_info': gap_info,
        'eligibility': eligibility,
        'existing_application': existing_application,
    }
    return render(request, 'internships/detail.html', context)


@login_required
def apply_view(request, pk):
    if not request.user.is_student:
        messages.error(request, "Only students can apply to internships and job postings.")
        return redirect('internships:detail', pk=pk)

    posting = get_object_or_404(InternshipPosting, pk=pk, is_active=True)
    student_profile = request.user.student_profile

    # Check existing application
    if Application.objects.filter(posting=posting, student=student_profile).exists():
        messages.warning(request, "You have already submitted an application for this role.")
        return redirect('internships:detail', pk=pk)

    # Automated check
    gap_info = calculate_skill_gap(student_profile, posting)
    eligibility = check_placement_eligibility(student_profile, posting, gap_info['match_percentage'])

    # Create application with snapshot of match percentage
    app = Application.objects.create(
        posting=posting,
        student=student_profile,
        match_percentage_at_apply=gap_info['match_percentage'],
        status='APPLIED'
    )

    # Automated in-app notifications
    create_notification(
        recipient=posting.company.user,
        title=f"New Candidate Applied: {posting.title}",
        message=f"{student_profile.user.get_full_name() or student_profile.user.username} ({student_profile.branch}) applied with a {gap_info['match_percentage']}% skill match.",
        notification_type='APPLICATION_UPDATE',
        link=f"/internships/postings/{posting.id}/applicants/"
    )

    create_notification(
        recipient=request.user,
        title=f"Application Received: {posting.title}",
        message=f"Your application to {posting.company.company_name} was received successfully.",
        notification_type='APPLICATION_UPDATE',
        link="/internships/my-applications/"
    )

    messages.success(request, f"Application submitted successfully! Your skill match score is {gap_info['match_percentage']}%.")
    return redirect('internships:my_applications')


@login_required
def create_posting_view(request):
    if not request.user.is_company:
        messages.error(request, "Only companies can post internship opportunities.")
        return redirect('accounts:dashboard')

    company_profile = request.user.company_profile
    all_skills = Skill.objects.all().order_by('name')

    if request.method == 'POST':
        form = InternshipPostingForm(request.POST)
        if form.is_valid():
            posting = form.save(commit=False)
            posting.company = company_profile
            posting.save()

            # Process selected required skills from POST
            skill_ids = request.POST.getlist('skills')
            for sid in skill_ids:
                prof = request.POST.get(f'prof_{sid}', 'INTERMEDIATE')
                mand = request.POST.get(f'mand_{sid}') == 'on'
                try:
                    skill_obj = Skill.objects.get(pk=sid)
                    PostingRequiredSkill.objects.create(
                        posting=posting,
                        skill=skill_obj,
                        minimum_proficiency=prof,
                        is_mandatory=mand
                    )
                except Skill.DoesNotExist:
                    continue

            # Notify students whose skills match >= 60%
            students = StudentProfile.objects.all()
            for s in students:
                gap = calculate_skill_gap(s, posting)
                if gap['match_percentage'] >= 60.0:
                    create_notification(
                        recipient=s.user,
                        title=f"New Matching Opportunity: {posting.title}",
                        message=f"{company_profile.company_name} posted a role matching {gap['match_percentage']}% of your skill profile!",
                        notification_type='NEW_MATCH',
                        link=f"/internships/{posting.id}/"
                    )

            messages.success(request, f"Posting '{posting.title}' published successfully!")
            return redirect('internships:company_postings')
    else:
        form = InternshipPostingForm()

    return render(request, 'internships/create_posting.html', {'form': form, 'all_skills': all_skills})


@login_required
def company_postings_view(request):
    if not request.user.is_company:
        return redirect('accounts:dashboard')

    company_profile = request.user.company_profile
    postings = InternshipPosting.objects.filter(company=company_profile).annotate()
    return render(request, 'internships/company_postings.html', {'postings': postings})


@login_required
def manage_applicants_view(request, pk):
    if not request.user.is_company:
        return redirect('accounts:dashboard')

    posting = get_object_or_404(InternshipPosting, pk=pk, company=request.user.company_profile)
    # Rank candidates by match percentage descending!
    applications = posting.applications.select_related('student__user').prefetch_related('student__skills__skill').order_by('-match_percentage_at_apply')
    
    return render(request, 'internships/manage_applicants.html', {
        'posting': posting,
        'applications': applications,
    })


@login_required
def update_application_status_view(request, pk):
    if not request.user.is_company:
        return redirect('accounts:dashboard')

    application = get_object_or_404(Application, pk=pk, posting__company=request.user.company_profile)
    
    if request.method == 'POST':
        form = ApplicationStatusUpdateForm(request.POST, instance=application)
        if form.is_valid():
            updated_app = form.save()

            # Automated Notification to student
            msg = f"Your application status for {updated_app.posting.title} was updated to: {updated_app.get_status_display()}."
            if updated_app.status == 'INTERVIEW_SCHEDULED' and updated_app.interview_date:
                msg = f"Interview Scheduled! Date: {updated_app.interview_date.strftime('%d %b %Y %I:%M %p')}. Venue/Link: {updated_app.interview_link_or_venue}"
            
            create_notification(
                recipient=updated_app.student.user,
                title=f"Application Update: {updated_app.posting.title}",
                message=msg,
                notification_type='INTERVIEW_SCHEDULED' if updated_app.status == 'INTERVIEW_SCHEDULED' else 'APPLICATION_UPDATE',
                link="/internships/my-applications/"
            )

            # If selected and placement, record placement
            if updated_app.status == 'SELECTED':
                PlacementRecord.objects.get_or_create(
                    student=updated_app.student,
                    company=updated_app.posting.company,
                    job_role=updated_app.posting.title,
                    defaults={'package_lpa': 8.00, 'acceptance_status': 'ACCEPTED'}
                )

            messages.success(request, f"Status updated for {updated_app.student.user.get_full_name() or updated_app.student.user.username} to '{updated_app.get_status_display()}'.")
            return redirect('internships:manage_applicants', pk=updated_app.posting.id)
    else:
        form = ApplicationStatusUpdateForm(instance=application)

    return render(request, 'internships/update_application_modal.html', {
        'form': form,
        'application': application
    })


@login_required
def my_applications_view(request):
    if not request.user.is_student:
        return redirect('accounts:dashboard')

    student_profile = request.user.student_profile
    applications_qs = Application.objects.filter(student=student_profile).select_related('posting__company').order_by('-applied_date')
    
    apps_with_live = []
    for app in applications_qs:
        gap = calculate_skill_gap(student_profile, app.posting)
        apps_with_live.append({
            'app': app,
            'current_match': gap['match_percentage']
        })

    return render(request, 'internships/my_applications.html', {'applications': apps_with_live})
