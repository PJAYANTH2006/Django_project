from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User, StudentProfile, CompanyProfile, FacultyProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Custom Role', {'fields': ('role',)}),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'registration_no', 'branch', 'cgpa', 'graduation_year')
    search_fields = ('user__username', 'registration_no', 'branch')
    list_filter = ('branch', 'graduation_year')

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'industry_type', 'location', 'is_verified')
    search_fields = ('company_name', 'industry_type')
    list_filter = ('is_verified', 'industry_type')

@admin.register(FacultyProfile)
class FacultyProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'designation', 'employee_id')
    search_fields = ('user__username', 'department', 'employee_id')
