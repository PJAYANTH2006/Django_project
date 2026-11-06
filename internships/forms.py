from django import forms
from internships.models import InternshipPosting, PostingRequiredSkill, Application
from skills.models import Skill

class InternshipPostingForm(forms.ModelForm):
    class Meta:
        model = InternshipPosting
        fields = [
            'title', 'posting_type', 'description', 'responsibilities',
            'location', 'stipend_or_salary', 'min_cgpa', 'allowed_branches',
            'open_positions', 'deadline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Backend Python Developer Intern'}),
            'posting_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Role description, mission, and scope...'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Key daily tasks & expectations...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Bangalore (Hybrid) / Remote'}),
            'stipend_or_salary': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ₹25,000 / month or ₹10 LPA'}),
            'min_cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10'}),
            'allowed_branches': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Comma-separated branches'}),
            'open_positions': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class AddPostingSkillForm(forms.ModelForm):
    class Meta:
        model = PostingRequiredSkill
        fields = ['skill', 'minimum_proficiency', 'is_mandatory']
        widgets = {
            'skill': forms.Select(attrs={'class': 'form-select'}),
            'minimum_proficiency': forms.Select(attrs={'class': 'form-select'}),
            'is_mandatory': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ApplicationStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'interview_date', 'interview_mode', 'interview_link_or_venue', 'company_feedback']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'interview_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'interview_mode': forms.Select(attrs={'class': 'form-select'}),
            'interview_link_or_venue': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Google Meet link or Room 204 Placement Cell'}),
            'company_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notes for candidate / review score'}),
        }
