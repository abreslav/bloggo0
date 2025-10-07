"""
Endpoint tests for django_app.views module.
"""
import pytest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User


class TestHomeView(TestCase):
    """
    Endpoint tests for home view.
    Test kind: endpoint_tests
    Original method: home
    """

    def setUp(self):
        """Set up test client."""
        self.client = Client()

    @pytest.mark.timeout(30)
    def test_home_view_returns_200_for_anonymous_user(self):
        """Test that home view returns 200 status for anonymous users."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(30)
    def test_home_view_uses_correct_template(self):
        """Test that home view uses the home.html template."""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    @pytest.mark.timeout(30)
    def test_home_view_shows_not_logged_in_message_for_anonymous_user(self):
        """Test that home view shows 'You are not logged in' for anonymous users."""
        response = self.client.get('/')
        self.assertContains(response, 'You are not logged in')
        self.assertContains(response, 'Authentication Status: Anonymous')

    @pytest.mark.timeout(30)
    def test_home_view_shows_google_login_button_for_anonymous_user(self):
        """Test that home view shows Google login button for anonymous users."""
        response = self.client.get('/')
        self.assertContains(response, 'Get Started with Google')
        # Check for the form action URL
        self.assertContains(response, 'google_login')

    @pytest.mark.timeout(30)
    def test_home_view_returns_200_for_authenticated_user(self):
        """Test that home view returns 200 status for authenticated users."""
        # Create and login a user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(user)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    @pytest.mark.timeout(30)
    def test_home_view_shows_welcome_message_for_authenticated_user(self):
        """Test that home view shows welcome message for authenticated users."""
        # Create and login a user with first name
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            first_name='John',
            password='testpass123'
        )
        self.client.force_login(user)

        response = self.client.get('/')
        self.assertContains(response, 'Hello, John!')
        self.assertContains(response, 'Authentication Status: Logged In')
        self.assertContains(response, 'Welcome back to Bloggo. You\'re successfully signed in.')

    @pytest.mark.timeout(30)
    def test_home_view_shows_email_when_no_first_name_for_authenticated_user(self):
        """Test that home view shows email when user has no first name."""
        # Create and login a user without first name
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(user)

        response = self.client.get('/')
        self.assertContains(response, 'Hello, test@example.com!')

    @pytest.mark.timeout(30)
    def test_home_view_shows_default_greeting_when_no_name_or_email(self):
        """Test that home view shows 'there' when user has no first name or email."""
        # Create and login a user without first name or email
        user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_login(user)

        response = self.client.get('/')
        self.assertContains(response, 'Hello, there!')

    @pytest.mark.timeout(30)
    def test_home_view_contains_common_content(self):
        """Test that home view contains common content regardless of authentication status."""
        # Test for anonymous user
        response = self.client.get('/')
        self.assertContains(response, 'Welcome to')
        self.assertContains(response, 'Bloggo')
        self.assertContains(response, 'A simple and elegant blogging platform')

        # Test for authenticated user
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(user)

        response = self.client.get('/')
        self.assertContains(response, 'Welcome to')
        self.assertContains(response, 'Bloggo')
        self.assertContains(response, 'A simple and elegant blogging platform')

    @pytest.mark.timeout(30)
    def test_home_view_does_not_show_login_button_for_authenticated_user(self):
        """Test that home view doesn't show login button for authenticated users."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(user)

        response = self.client.get('/')
        self.assertNotContains(response, 'Get Started with Google')
        self.assertNotContains(response, 'You are not logged in')

    @pytest.mark.timeout(30)
    def test_home_view_uses_home_html_template_with_authenticated_user(self):
        """Test that home view uses home.html template for authenticated users."""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(user)

        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')