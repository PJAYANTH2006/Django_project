from django import forms
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, CompanyProfile, FacultyProfile

User = get_user_model()

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create Password'}), min_length=6)
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match.')
        return cleaned_data


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['registration_no', 'branch', 'cgpa', 'graduation_year', 'bio', 'phone', 'github_url', 'linkedin_url', 'resume']
        widgets = {
            'registration_no': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2023CSE045'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '10'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief professional summary / career objectives...'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/username'}),
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.txt'}),
        }


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['company_name', 'industry_type', 'website', 'location', 'description', 'contact_email']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'industry_type': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
