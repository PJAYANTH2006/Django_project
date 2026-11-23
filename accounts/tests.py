from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='password123', role='STUDENT')

    def test_logout_via_post(self):
        self.client.login(username='tester', password='password123')
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        # Verify user is logged out
        dashboard_response = self.client.get(reverse('accounts:dashboard'))
        self.assertEqual(dashboard_response.status_code, 302) # redirects to login

    def test_logout_via_get(self):
        self.client.login(username='tester', password='password123')
        response = self.client.get(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
