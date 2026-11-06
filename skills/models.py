from django.db import models
from accounts.models import StudentProfile


class SkillCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(max_length=50, default='bi-code-slash', help_text='Bootstrap icon class')

    class Meta:
        verbose_name_plural = 'Skill Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='skills')
    description = models.TextField(blank=True)
    aliases = models.CharField(max_length=255, blank=True, help_text="Comma-separated keywords for resume parsing (e.g. 'js, es6, javascript')")

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class StudentSkill(models.Model):
    PROFICIENCY_CHOICES = (
        ('BEGINNER', 'Beginner (Basic Knowledge)'),
        ('INTERMEDIATE', 'Intermediate (Hands-on Projects)'),
        ('ADVANCED', 'Advanced (Production Ready)'),
    )

    PROFICIENCY_WEIGHTS = {
        'BEGINNER': 1,
        'INTERMEDIATE': 2,
        'ADVANCED': 3,
    }

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='student_associations')
    proficiency = models.CharField(max_length=20, choices=PROFICIENCY_CHOICES, default='INTERMEDIATE')
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'skill')
        ordering = ['-proficiency', 'skill__name']

    @property
    def weight(self):
        return self.PROFICIENCY_WEIGHTS.get(self.proficiency, 1)

    def __str__(self):
        return f"{self.student.user.username} - {self.skill.name} ({self.get_proficiency_display()})"


class StudentProject(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='projects')
    title = models.CharField(max_length=200)
    description = models.TextField()
    technologies_used = models.CharField(max_length=255, help_text="e.g. Python, Django, React, PostgreSQL")
    github_link = models.URLField(blank=True)
    live_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.student.user.username}"


class StudentCertification(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='certifications')
    title = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=200)
    issue_date = models.DateField(null=True, blank=True)
    credential_url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.issuing_organization})"


class SkillResource(models.Model):
    RESOURCE_TYPES = (
        ('DOCUMENTATION', 'Official Documentation'),
        ('COURSE', 'Free Course / Guided Tutorial'),
        ('PROJECT_IDEA', 'Recommended Capstone Project Idea'),
    )
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    resource_url = models.URLField(max_length=500)
    resource_type = models.CharField(max_length=30, choices=RESOURCE_TYPES, default='COURSE')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.skill.name} - {self.title} [{self.get_resource_type_display()}]"
