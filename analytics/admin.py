from django.contrib import admin
from analytics.models import CampusNotice

@admin.register(CampusNotice)
class CampusNoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'notice_type', 'posted_by', 'is_active', 'created_at')
    list_filter = ('notice_type', 'is_active')
    search_fields = ('title', 'content', 'posted_by__username')
