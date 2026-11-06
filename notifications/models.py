from django.db import models
from django.conf import settings


class Notification(models.Model):
    TYPE_CHOICES = (
        ('APPLICATION_UPDATE', 'Application Status Update'),
        ('INTERVIEW_SCHEDULED', 'Interview Scheduled'),
        ('NEW_MATCH', 'Matching Internship Posted'),
        ('SKILL_GAP', 'Skill Gap Alert'),
        ('SYSTEM', 'System Announcement'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='SYSTEM')
    link = models.CharField(max_length=300, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.username}: {self.title}"


def create_notification(recipient, title, message, notification_type='SYSTEM', link=''):
    """Helper to dispatch in-app notifications easily anywhere in the codebase."""
    return Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        notification_type=notification_type,
        link=link
    )
