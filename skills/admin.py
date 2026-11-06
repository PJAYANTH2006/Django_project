from django.contrib import admin
from skills.models import SkillCategory, Skill, StudentSkill, SkillResource, StudentProject, StudentCertification

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1

@admin.register(SkillCategory)
class SkillCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')
    inlines = [SkillInline]

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'aliases')
    search_fields = ('name', 'aliases')
    list_filter = ('category',)

@admin.register(StudentSkill)
class StudentSkillAdmin(admin.ModelAdmin):
    list_display = ('student', 'skill', 'proficiency', 'verified', 'created_at')
    list_filter = ('proficiency', 'verified', 'skill__category')
    search_fields = ('student__user__username', 'skill__name')

@admin.register(SkillResource)
class SkillResourceAdmin(admin.ModelAdmin):
    list_display = ('skill', 'title', 'resource_type', 'resource_url')
    list_filter = ('resource_type', 'skill__category')
    search_fields = ('title', 'skill__name')

admin.site.register(StudentProject)
admin.site.register(StudentCertification)
