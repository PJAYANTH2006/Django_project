from django import forms
from skills.models import StudentSkill, Skill, StudentProject, StudentCertification

class AddStudentSkillForm(forms.ModelForm):
    class Meta:
        model = StudentSkill
        fields = ['skill', 'proficiency']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'proficiency': forms.Select(attrs={'class': 'form-select'}),
        }


class StudentProjectForm(forms.ModelForm):
    class Meta:
        model = StudentProject
        fields = ['title', 'description', 'technologies_used', 'github_link', 'live_link']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'What problem did it solve? Key achievements...'}),
            'technologies_used': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Python, Django, PostgreSQL, Docker'}),
            'github_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/...'}),
            'live_link': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }


class StudentCertificationForm(forms.ModelForm):
    class Meta:
        model = StudentCertification
        fields = ['title', 'issuing_organization', 'issue_date', 'credential_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Certification Title'}),
            'issuing_organization': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. AWS, Coursera, Meta'}),
            'issue_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'credential_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'Verification URL'}),
        }


class ResumeUploadForm(forms.Form):
    resume_file = forms.FileField(
        label="Upload Resume (PDF or TXT)",
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.txt'}),
        help_text="Our smart parser will extract your technical skills automatically."
    )
