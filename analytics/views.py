from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from accounts.models import StudentProfile, CompanyProfile, FacultyProfile
from skills.models import Skill, StudentSkill, SkillCategory
from internships.models import InternshipPosting, PostingRequiredSkill, Application, PlacementRecord
from analytics.models import CampusNotice


@login_required
def faculty_overview_view(request):
    if not (request.user.is_faculty or request.user.is_superuser):
        return redirect('accounts:dashboard')

    if request.method == 'POST' and 'create_notice' in request.POST:
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        notice_type = request.POST.get('notice_type', 'GENERAL')
        if title and content:
            CampusNotice.objects.create(
                posted_by=request.user,
                title=title,
                content=content,
                notice_type=notice_type
            )
            messages.success(request, f"Notice '{title}' published successfully.")
            return redirect('analytics:faculty_overview')
        else:
            messages.error(request, "Please provide both a notice title and content.")

    total_students = StudentProfile.objects.count()
    total_companies = CompanyProfile.objects.count()
    total_postings = InternshipPosting.objects.filter(is_active=True).count()
    total_placements = PlacementRecord.objects.count()

    placement_percentage = round((total_placements / total_students * 100.0), 1) if total_students > 0 else 0
    avg_package = PlacementRecord.objects.aggregate(Avg('package_lpa'))['package_lpa__avg'] or 0

    # Skill Gap institutional intelligence:
    # Top required skills by industry vs how many students possess them
    skill_market_data = (
        PostingRequiredSkill.objects.values('skill__name')
        .annotate(demand_count=Count('id'))
        .order_by('-demand_count')[:8]
    )

    skill_names = []
    demand_counts = []
    supply_counts = []

    for item in skill_market_data:
        s_name = item['skill__name']
        skill_names.append(s_name)
        demand_counts.append(item['demand_count'])
        student_count = StudentSkill.objects.filter(skill__name=s_name).count()
        supply_counts.append(student_count)

    # Application funnel statistics
    status_counts = {
        'APPLIED': Application.objects.filter(status='APPLIED').count(),
        'UNDER_REVIEW': Application.objects.filter(status='UNDER_REVIEW').count(),
        'SHORTLISTED': Application.objects.filter(status='SHORTLISTED').count(),
        'INTERVIEW_SCHEDULED': Application.objects.filter(status='INTERVIEW_SCHEDULED').count(),
        'SELECTED': Application.objects.filter(status='SELECTED').count(),
    }

    # Branch distribution
    branch_stats = (
        StudentProfile.objects.values('branch')
        .annotate(student_count=Count('id'))
        .order_by('-student_count')
    )

    # Recent placements
    recent_placements = PlacementRecord.objects.select_related('student__user', 'company').order_by('-offer_date')[:5]

    # Campus Notices
    notices = CampusNotice.objects.filter(is_active=True).order_by('-created_at')[:6]

    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_postings': total_postings,
        'total_placements': total_placements,
        'placement_percentage': placement_percentage,
        'avg_package': round(avg_package, 2),
        'skill_names': skill_names,
        'demand_counts': demand_counts,
        'supply_counts': supply_counts,
        'status_counts': status_counts,
        'branch_stats': branch_stats,
        'recent_placements': recent_placements,
        'notices': notices,
    }
    return render(request, 'analytics/faculty_overview.html', context)


@login_required
def student_readiness_view(request):
    """
    Search and filter student talent pool for faculty placement coordinator.
    """
    if not (request.user.is_faculty or request.user.is_superuser or request.user.is_company):
        return redirect('accounts:dashboard')

    branch_filter = request.GET.get('branch', '')
    min_cgpa = request.GET.get('min_cgpa', '')
    skill_filter = request.GET.get('skill', '')

    students_qs = StudentProfile.objects.select_related('user').prefetch_related('skills__skill')

    if branch_filter:
        students_qs = students_qs.filter(branch=branch_filter)
    if min_cgpa:
        try:
            students_qs = students_qs.filter(cgpa__gte=float(min_cgpa))
        except ValueError:
            pass
    if skill_filter:
        students_qs = students_qs.filter(skills__skill__name__icontains=skill_filter)

    branches = StudentProfile.BRANCH_CHOICES
    all_skills = Skill.objects.all().order_by('name')

    context = {
        'students': students_qs.distinct(),
        'branches': branches,
        'all_skills': all_skills,
        'selected_branch': branch_filter,
        'selected_cgpa': min_cgpa,
        'selected_skill': skill_filter,
    }
    return render(request, 'analytics/student_readiness.html', context)


@login_required
def api_skill_stats_view(request):
    skill_market_data = (
        PostingRequiredSkill.objects.values('skill__name')
        .annotate(demand=Count('id'))
        .order_by('-demand')[:10]
    )
    labels = [d['skill__name'] for d in skill_market_data]
    demand_data = [d['demand'] for d in skill_market_data]
    supply_data = [StudentSkill.objects.filter(skill__name=s).count() for s in labels]

    return JsonResponse({
        'labels': labels,
        'demand': demand_data,
        'supply': supply_data,
    })


@login_required
def api_placement_stats_view(request):
    funnel = [
        Application.objects.filter(status='APPLIED').count(),
        Application.objects.filter(status='UNDER_REVIEW').count(),
        Application.objects.filter(status='SHORTLISTED').count(),
        Application.objects.filter(status='INTERVIEW_SCHEDULED').count(),
        Application.objects.filter(status='SELECTED').count(),
    ]
    return JsonResponse({
        'labels': ['Applied', 'Under Review', 'Shortlisted', 'Interview Scheduled', 'Selected / Placed'],
        'data': funnel,
    })
