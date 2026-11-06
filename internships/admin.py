from django.contrib import admin
from internships.models import InternshipPosting, PostingRequiredSkill, Application, PlacementRecord

class RequiredSkillInline(admin.TabularInline):
    model = PostingRequiredSkill
    extra = 1

@admin.register(InternshipPosting)
class InternshipPostingAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'posting_type', 'location', 'min_cgpa', 'is_active', 'deadline')
    list_filter = ('posting_type', 'is_active', 'company')
    search_fields = ('title', 'company__company_name', 'description')
    inlines = [RequiredSkillInline]

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'posting', 'match_percentage_at_apply', 'status', 'applied_date')
    list_filter = ('status', 'posting__company')
    search_fields = ('student__user__username', 'posting__title')

@admin.register(PlacementRecord)
class PlacementRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'company', 'job_role', 'package_lpa', 'offer_date', 'acceptance_status')
    list_filter = ('acceptance_status', 'company')
    search_fields = ('student__user__username', 'company__company_name', 'job_role')
