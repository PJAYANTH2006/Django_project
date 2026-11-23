from django.db import models
from django.conf import settings


class CampusNotice(models.Model):
    NOTICE_TYPES = (
        ('PLACEMENT', 'Placement Drive'),
        ('ACADEMIC', 'Academic / Examination'),
        ('WORKSHOP', 'Faculty & Student Workshop'),
        ('GENERAL', 'General Announcement'),
    )

    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posted_notices')
    title = models.CharField(max_length=200)
    content = models.TextField()
    notice_type = models.CharField(max_length=30, choices=NOTICE_TYPES, default='GENERAL')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
