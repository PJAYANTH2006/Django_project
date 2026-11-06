from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from decimal import Decimal
from accounts.models import StudentProfile, CompanyProfile
from skills.models import SkillCategory, Skill, StudentSkill
from internships.models import InternshipPosting, PostingRequiredSkill, Application
from notifications.models import Notification

User = get_user_model()

class ApplicationWorkflowTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Users
        self.student_user = User.objects.create_user(username='student1', password='password123', role='STUDENT')
        self.student_profile = StudentProfile.objects.create(
            user=self.student_user,
            branch='Computer Science & Engineering',
            cgpa=Decimal('8.00')
        )

        self.company_user = User.objects.create_user(username='company1', password='password123', role='COMPANY')
        self.company_profile = CompanyProfile.objects.create(user=self.company_user, company_name='Tech Dynamics')

        # Skill & Posting
        cat = SkillCategory.objects.create(name='Languages')
        skill = Skill.objects.create(name='Python', category=cat)
        StudentSkill.objects.create(student=self.student_profile, skill=skill, proficiency='ADVANCED')

        self.posting = InternshipPosting.objects.create(
            company=self.company_profile,
            title='Python Intern',
            min_cgpa=Decimal('7.00'),
            allowed_branches='Computer Science & Engineering',
            deadline='2026-12-31'
        )
        PostingRequiredSkill.objects.create(posting=self.posting, skill=skill, minimum_proficiency='INTERMEDIATE')

    def test_apply_and_notification_flow(self):
        # Log in as student
        self.client.login(username='student1', password='password123')

        # Apply
        response = self.client.get(reverse('internships:apply', kwargs={'pk': self.posting.id}))
        self.assertEqual(response.status_code, 302)

        # Check application created
        app = Application.objects.get(posting=self.posting, student=self.student_profile)
        self.assertEqual(app.status, 'APPLIED')
        self.assertEqual(app.match_percentage_at_apply, 100.0)

        # Check notification sent to company
        company_notifs = Notification.objects.filter(recipient=self.company_user)
        self.assertTrue(company_notifs.exists())

        # Now company logs in and schedules interview
        self.client.logout()
        self.client.login(username='company1', password='password123')

        update_response = self.client.post(
            reverse('internships:update_status', kwargs={'pk': app.id}),
            {
                'status': 'INTERVIEW_SCHEDULED',
                'interview_mode': 'ONLINE',
                'interview_link_or_venue': 'https://meet.google.com/test-room',
                'company_feedback': 'Strong Python knowledge. Proceeding to interview round.'
            }
        )
        self.assertEqual(update_response.status_code, 302)

        app.refresh_from_db()
        self.assertEqual(app.status, 'INTERVIEW_SCHEDULED')
        self.assertEqual(app.interview_link_or_venue, 'https://meet.google.com/test-room')

        # Check student received interview notification
        student_notifs = Notification.objects.filter(recipient=self.student_user, notification_type='INTERVIEW_SCHEDULED')
        self.assertTrue(student_notifs.exists())
