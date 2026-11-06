from django.db import models
from accounts.models import CompanyProfile, StudentProfile
from skills.models import Skill


class InternshipPosting(models.Model):
    POSTING_TYPES = (
        ('INTERNSHIP', 'Internship'),
        ('FULL_TIME', 'Full-Time Job'),
        ('PLACEMENT', 'Campus Placement Drive'),
    )

    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='postings')
    title = models.CharField(max_length=200)
    posting_type = models.CharField(max_length=20, choices=POSTING_TYPES, default='INTERNSHIP')
    description = models.TextField()
    responsibilities = models.TextField(blank=True)
    location = models.CharField(max_length=150, default='Bangalore / Remote')
    stipend_or_salary = models.CharField(max_length=100, default='₹25,000 / month')
    min_cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=6.50)
    allowed_branches = models.TextField(
        default='Computer Science & Engineering, Information Technology, Artificial Intelligence & Data Science',
        help_text='Comma-separated allowed branches'
    )
    open_positions = models.PositiveIntegerField(default=3)
    deadline = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

    def get_allowed_branches_list(self):
        return [b.strip() for b in self.allowed_branches.split(',') if b.strip()]


class PostingRequiredSkill(models.Model):
    PROFICIENCY_CHOICES = (
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
    )

    PROFICIENCY_WEIGHTS = {
        'BEGINNER': 1,
        'INTERMEDIATE': 2,
        'ADVANCED': 3,
    }

    posting = models.ForeignKey(InternshipPosting, on_delete=models.CASCADE, related_name='required_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='posting_requirements')
    minimum_proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='INTERMEDIATE')
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        unique_together = ('posting', 'skill')

    @property
    def weight(self):
        return self.PROFICIENCY_WEIGHTS.get(self.minimum_proficiency, 2)

    def __str__(self):
        return f"{self.posting.title} - {self.skill.name} ({self.minimum_proficiency})"


class Application(models.Model):
    STATUS_CHOICES = (
        ('APPLIED', 'Applied'),
        ('UNDER_REVIEW', 'Under Review'),
        ('SHORTLISTED', 'Shortlisted'),
        ('INTERVIEW_SCHEDULED', 'Interview Scheduled'),
        ('SELECTED', 'Selected / Offered'),
        ('REJECTED', 'Not Selected'),
    )

    posting = models.ForeignKey(InternshipPosting, on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='applications')
    match_percentage_at_apply = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='APPLIED')
    applied_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Interview scheduling details
    interview_date = models.DateTimeField(null=True, blank=True)
    interview_mode = models.CharField(
        max_length=20,
        choices=(('ONLINE', 'Online Video Call'), ('OFFLINE', 'In-Person / Campus')),
        blank=True
    )
    interview_link_or_venue = models.CharField(max_length=300, blank=True)
    company_feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('posting', 'student')
        ordering = ['-applied_date']

    def __str__(self):
        return f"{self.student.user.username} applied to {self.posting.title} [{self.status}]"


class PlacementRecord(models.Model):
    STATUS_CHOICES = (
        ('OFFERED', 'Offered'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
    )

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='placements')
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='hired_students')
    job_role = models.CharField(max_length=200)
    package_lpa = models.DecimalField(max_digits=5, decimal_places=2, help_text="Annual CTC in Lakhs (e.g. 8.50)")
    offer_date = models.DateField(auto_now_add=True)
    acceptance_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACCEPTED')

    class Meta:
        ordering = ['-offer_date']

    def __str__(self):
        return f"{self.student.user.username} - {self.job_role} @ {self.company.company_name} ({self.package_lpa} LPA)"
