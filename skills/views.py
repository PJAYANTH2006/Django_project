from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from skills.models import Skill, StudentSkill, SkillCategory, SkillResource, StudentProject, StudentCertification
from skills.forms import AddStudentSkillForm, StudentProjectForm, StudentCertificationForm, ResumeUploadForm
from skills.automation import (
    calculate_skill_gap,
    check_placement_eligibility,
    extract_skills_from_text,
    extract_text_from_pdf_file
)
from internships.models import InternshipPosting, Application
from accounts.models import StudentProfile


@login_required
def my_skills_view(request):
    if not request.user.is_student:
        messages.warning(request, "Skill mapping is specifically for students.")
        return redirect('accounts:dashboard')

    student_profile = request.user.student_profile
    student_skills = StudentSkill.objects.filter(student=student_profile).select_related('skill', 'skill__category')
    categories = SkillCategory.objects.prefetch_related('skills').all()
    form = AddStudentSkillForm()
    project_form = StudentProjectForm()
    cert_form = StudentCertificationForm()

    context = {
        'student': student_profile,
        'student_skills': student_skills,
        'categories': categories,
        'form': form,
        'project_form': project_form,
        'cert_form': cert_form,
        'projects': student_profile.projects.all(),
        'certifications': student_profile.certifications.all(),
    }
    return render(request, 'skills/my_skills.html', context)


@login_required
def add_skill_view(request):
    if not request.user.is_student:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = AddStudentSkillForm(request.POST)
        if form.is_valid():
            skill = form.cleaned_data['skill']
            proficiency = form.cleaned_data['proficiency']
            obj, created = StudentSkill.objects.update_or_create(
                student=request.user.student_profile,
                skill=skill,
                defaults={'proficiency': proficiency}
            )
            if created:
                messages.success(request, f"Added {skill.name} ({obj.get_proficiency_display()}) to your profile!")
            else:
                messages.info(request, f"Updated proficiency for {skill.name} to {obj.get_proficiency_display()}.")
        else:
            messages.error(request, "Error adding skill. Please check your selection.")

    return redirect('skills:my_skills')


@login_required
def delete_skill_view(request, pk):
    if not request.user.is_student:
        return redirect('accounts:dashboard')

    skill_entry = get_object_or_404(StudentSkill, pk=pk, student=request.user.student_profile)
    skill_name = skill_entry.skill.name
    skill_entry.delete()
    messages.info(request, f"Removed {skill_name} from your skills.")
    return redirect('skills:my_skills')


@login_required
def resume_upload_view(request):
    """
    Smart Automation: Automated Resume Skill Extractor.
    Extracts text from PDF/TXT resume, matches against skill catalog,
    and allows student to auto-import detected skills.
    """
    if not request.user.is_student:
        return redirect('accounts:dashboard')

    student_profile = request.user.student_profile
    detected_skills = []
    already_owned_ids = set(student_profile.skills.values_list('skill_id', flat=True))

    if request.method == 'POST':
        if 'import_skills' in request.POST:
            # Handle bulk skill import of detected skills
            selected_skill_ids = request.POST.getlist('selected_skills')
            imported_count = 0
            for sid in selected_skill_ids:
                try:
                    skill = Skill.objects.get(pk=sid)
                    StudentSkill.objects.get_or_create(
                        student=student_profile,
                        skill=skill,
                        defaults={'proficiency': 'INTERMEDIATE', 'verified': True}
                    )
                    imported_count += 1
                except Skill.DoesNotExist:
                    continue
            messages.success(request, f"Successfully imported {imported_count} extracted skills into your profile!")
            return redirect('skills:my_skills')

        form = ResumeUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['resume_file']
            # Save to profile
            student_profile.resume = uploaded_file
            
            # Extract text
            raw_text = extract_text_from_pdf_file(uploaded_file)
            student_profile.resume_extracted_text = raw_text[:5000] # store first 5k chars
            student_profile.save()

            # Rule-based NLP extraction
            skills_found = extract_skills_from_text(raw_text)

            detected_skills = [
                {
                    'skill': s,
                    'already_added': s.id in already_owned_ids
                }
                for s in skills_found
            ]
            new_count = sum(1 for d in detected_skills if not d['already_added'])
            messages.success(request, f"Resume parsed! Identified {len(detected_skills)} skills ({new_count} new to import).")
    else:
        form = ResumeUploadForm()

    context = {
        'form': form,
        'student': student_profile,
        'detected_skills': detected_skills,
    }
    return render(request, 'skills/resume_upload.html', context)


@login_required
def gap_analysis_view(request, posting_id):
    """
    Smart Automation: Real-time Skill Gap Analysis Dashboard.
    Compares student's skills against posting's required skills.
    Shows exact gaps and roadmap resources.
    """
    posting = get_object_or_404(InternshipPosting, pk=posting_id)
    existing_application = None
    
    if request.user.is_student:
        student_profile = request.user.student_profile
        existing_application = Application.objects.filter(posting=posting, student=student_profile).first()
    else:
        # If faculty or company, optionally view as a demo with first student
        student_profile = StudentProfile.objects.first()

    gap_data = calculate_skill_gap(student_profile, posting)
    eligibility_data = check_placement_eligibility(student_profile, posting, gap_data['match_percentage'])

    context = {
        'posting': posting,
        'student': student_profile,
        'gap': gap_data,
        'eligibility': eligibility_data,
        'existing_application': existing_application,
    }
    return render(request, 'skills/gap_analysis.html', context)


def explore_skills_view(request):
    categories = SkillCategory.objects.prefetch_related('skills__resources').all()
    student_skill_ids = set()
    if request.user.is_authenticated and request.user.is_student:
        student_skill_ids = set(request.user.student_profile.skills.values_list('skill_id', flat=True))

    return render(request, 'skills/explore.html', {
        'categories': categories,
        'student_skill_ids': student_skill_ids,
    })
