from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty / Admin'),
        ('COMPANY', 'Industry / Company'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')

    @property
    def is_student(self):
        return self.role == 'STUDENT'

    @property
    def is_faculty(self):
        return self.role == 'FACULTY'

    @property
    def is_company(self):
        return self.role == 'COMPANY'

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    BRANCH_CHOICES = (
        ('Computer Science & Engineering', 'Computer Science & Engineering'),
        ('Information Technology', 'Information Technology'),
        ('Artificial Intelligence & Data Science', 'Artificial Intelligence & Data Science'),
        ('Electronics & Communication Engineering', 'Electronics & Communication Engineering'),
        ('Electrical & Electronics Engineering', 'Electrical & Electronics Engineering'),
        ('Mechanical Engineering', 'Mechanical Engineering'),
        ('Civil Engineering', 'Civil Engineering'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registration_no = models.CharField(max_length=50, blank=True)
    branch = models.CharField(max_length=100, choices=BRANCH_CHOICES, default='Computer Science & Engineering')
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=7.50)
    graduation_year = models.PositiveIntegerField(default=2026)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    resume_extracted_text = models.TextField(blank=True, default='')
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.registration_no or self.branch}"


class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_name = models.CharField(max_length=200)
    industry_type = models.CharField(max_length=100, default='Information Technology')
    website = models.URLField(blank=True)
    location = models.CharField(max_length=150, default='Bangalore / Remote')
    description = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name or self.user.username


class FacultyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    department = models.CharField(max_length=100, default='Computer Science & Engineering')
    designation = models.CharField(max_length=100, default='Associate Professor & Placement Coordinator')
    employee_id = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.department})"
