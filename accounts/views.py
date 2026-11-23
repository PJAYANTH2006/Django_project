from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import User, StudentProfile, CompanyProfile, FacultyProfile
from accounts.forms import UserRegistrationForm, StudentProfileForm, CompanyProfileForm
from internships.models import InternshipPosting, Application, PlacementRecord
from skills.models import StudentSkill, Skill, StudentProject, StudentCertification
from skills.automation import get_recommended_postings_for_student, calculate_skill_gap
from notifications.models import Notification
from analytics.models import CampusNotice


def home_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    total_students = StudentProfile.objects.count()
    total_companies = CompanyProfile.objects.count()
    total_postings = InternshipPosting.objects.filter(is_active=True).count()
    total_placements = PlacementRecord.objects.count()

    recent_postings = InternshipPosting.objects.filter(is_active=True).select_related('company')[:4]

    context = {
        'total_students': total_students,
        'total_companies': total_companies,
        'total_postings': total_postings,
        'total_placements': total_placements,
        'recent_postings': recent_postings,
    }
    return render(request, 'accounts/home.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            return redirect('accounts:dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


def logout_view(request):
    if request.method in ['POST', 'GET']:
        logout(request)
        messages.info(request, "You have been logged out successfully.")
    return redirect('accounts:login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            # Create default profile based on chosen role
            if user.role == 'STUDENT':
                StudentProfile.objects.create(user=user)
            elif user.role == 'COMPANY':
                CompanyProfile.objects.create(user=user, company_name=user.username)
            elif user.role == 'FACULTY':
                FacultyProfile.objects.create(user=user)

            messages.success(request, "Account created successfully! Please login.")
            return redirect('accounts:login')
        else:
            messages.error(request, "Please correct the errors in the registration form.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard_view(request):
    user = request.user

    # 1. Faculty Dashboard Redirect
    if user.is_faculty or user.is_superuser:
        return redirect('analytics:faculty_overview')

    # 2. Company Dashboard
    if user.is_company:
        company_profile, _ = CompanyProfile.objects.get_or_create(user=user, defaults={'company_name': user.username})
        postings = InternshipPosting.objects.filter(company=company_profile)
        total_postings = postings.count()
        total_applicants = Application.objects.filter(posting__company=company_profile).count()
        shortlisted_applicants = Application.objects.filter(posting__company=company_profile, status='SHORTLISTED').count()
        scheduled_interviews = Application.objects.filter(
            posting__company=company_profile, 
            status='INTERVIEW_SCHEDULED'
        ).select_related('student__user', 'posting')[:5]

        recent_applications = Application.objects.filter(
            posting__company=company_profile
        ).select_related('student__user', 'posting').order_by('-applied_date')[:6]

        context = {
            'company': company_profile,
            'postings': postings,
            'total_postings': total_postings,
            'total_applicants': total_applicants,
            'shortlisted_applicants': shortlisted_applicants,
            'scheduled_interviews': scheduled_interviews,
            'recent_applications': recent_applications,
        }
        return render(request, 'accounts/company_dashboard.html', context)

    # 3. Student Dashboard
    student_profile, _ = StudentProfile.objects.get_or_create(user=user)
    student_skills = StudentSkill.objects.filter(student=student_profile).select_related('skill', 'skill__category')
    applications = Application.objects.filter(student=student_profile).select_related('posting__company')
    
    # Smart Recommendations Engine
    recommendations = get_recommended_postings_for_student(student_profile, limit=6)

    # Campus Notices
    campus_notices = CampusNotice.objects.filter(is_active=True).order_by('-created_at')[:3]

    context = {
        'student': student_profile,
        'student_skills': student_skills,
        'applications': applications,
        'recommendations': recommendations,
        'campus_notices': campus_notices,
        'total_skills': student_skills.count(),
        'total_applications': applications.count(),
        'projects': student_profile.projects.all(),
        'certifications': student_profile.certifications.all(),
    }
    return render(request, 'accounts/student_dashboard.html', context)


@login_required
def profile_view(request):
    user = request.user
    if user.is_student:
        student_profile, _ = StudentProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Student profile updated successfully!")
                return redirect('accounts:profile')
        else:
            form = StudentProfileForm(instance=student_profile)
        return render(request, 'accounts/student_profile.html', {
            'form': form,
            'student': student_profile,
            'skills': student_profile.skills.all(),
            'projects': student_profile.projects.all(),
            'certifications': student_profile.certifications.all(),
        })

    elif user.is_company:
        company_profile, _ = CompanyProfile.objects.get_or_create(user=user)
        if request.method == 'POST':
            form = CompanyProfileForm(request.POST, instance=company_profile)
            if form.is_valid():
                form.save()
                messages.success(request, "Company profile updated successfully!")
                return redirect('accounts:profile')
        else:
            form = CompanyProfileForm(instance=company_profile)
        return render(request, 'accounts/company_profile.html', {'form': form, 'company': company_profile})

    return redirect('accounts:dashboard')
