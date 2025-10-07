"""
Unit tests for django_app.signals module.
"""
import os
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from django.test import TestCase
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django_app.signals import _read_config_parameter, configure_social_apps


class TestReadConfigParameter(TestCase):
    """
    Unit tests for _read_config_parameter function.
    Test kind: unit_tests
    Original method: _read_config_parameter
    """

    @pytest.mark.timeout(30)
    def test_read_from_env_local_file_when_exists(self):
        """Test reading parameter from .env.local file when it exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Create .env.local file with test content
                env_local_path = Path(".env.local")
                env_local_path.write_text("TEST_PARAM=value_from_env_local\n")

                # Test case-insensitive reading
                result = _read_config_parameter("test_param")
                self.assertEqual(result, "value_from_env_local")

                # Test with uppercase parameter name
                result = _read_config_parameter("TEST_PARAM")
                self.assertEqual(result, "value_from_env_local")

            finally:
                os.chdir(original_cwd)

    @pytest.mark.timeout(30)
    def test_read_from_environment_when_env_local_not_exists(self):
        """Test reading parameter from environment variables when .env.local doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                with patch.dict(os.environ, {'TEST_ENV_PARAM': 'value_from_env'}):
                    result = _read_config_parameter("test_env_param")
                    self.assertEqual(result, "value_from_env")

                    # Test case-insensitive
                    result = _read_config_parameter("TEST_ENV_PARAM")
                    self.assertEqual(result, "value_from_env")

            finally:
                os.chdir(original_cwd)

    @pytest.mark.timeout(30)
    def test_env_local_takes_precedence_over_environment(self):
        """Test that .env.local file takes precedence over environment variables."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Create .env.local file
                env_local_path = Path(".env.local")
                env_local_path.write_text("PRIORITY_TEST=env_local_value\n")

                # Set environment variable with different value
                with patch.dict(os.environ, {'PRIORITY_TEST': 'env_value'}):
                    result = _read_config_parameter("priority_test")
                    self.assertEqual(result, "env_local_value")

            finally:
                os.chdir(original_cwd)

    @pytest.mark.timeout(30)
    def test_returns_none_when_parameter_not_found(self):
        """Test that function returns None when parameter is not found anywhere."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                result = _read_config_parameter("nonexistent_param")
                self.assertIsNone(result)

            finally:
                os.chdir(original_cwd)

    @pytest.mark.timeout(30)
    def test_parameter_name_case_conversion(self):
        """Test that parameter names are converted to uppercase."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)

            try:
                # Create .env.local with uppercase parameter
                env_local_path = Path(".env.local")
                env_local_path.write_text("CASE_TEST=test_value\n")

                # Test with lowercase input
                result = _read_config_parameter("case_test")
                self.assertEqual(result, "test_value")

                # Test with mixed case input
                result = _read_config_parameter("Case_Test")
                self.assertEqual(result, "test_value")

            finally:
                os.chdir(original_cwd)


class TestConfigureSocialApps(TestCase):
    """
    Unit tests for configure_social_apps function.
    Test kind: unit_tests
    Original method: configure_social_apps
    """

    @pytest.mark.timeout(30)
    def test_skips_when_sender_is_not_django_app(self):
        """Test that function returns early when sender is not django_app."""
        # Create a mock sender with different name
        mock_sender = MagicMock()
        mock_sender.name = "other_app"

        # Mock the Site and SocialApp models to ensure they're not called
        with patch('django_app.signals.Site') as mock_site, \
             patch('django_app.signals.SocialApp') as mock_social_app:

            configure_social_apps(sender=mock_sender)

            # Verify that no database operations were performed
            mock_site.objects.get_or_create.assert_not_called()
            mock_social_app.objects.get_or_create.assert_not_called()

    @pytest.mark.timeout(30)
    @patch('django_app.signals.SOCIAL_LOGIN_PROVIDERS', {
        'google': {
            'name': 'Google',
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret'
        }
    })
    def test_creates_social_app_with_valid_credentials(self):
        """Test that SocialApp is created when valid credentials are provided."""
        mock_sender = MagicMock()
        mock_sender.name = "django_app"

        # Mock the Site model
        mock_site = MagicMock()
        mock_site.id = 1

        # Mock the SocialApp model
        mock_social_app = MagicMock()
        mock_social_app.sites = MagicMock()

        with patch('django_app.signals.Site') as mock_site_class, \
             patch('django_app.signals.SocialApp') as mock_social_app_class, \
             patch('builtins.print') as mock_print:

            mock_site_class.objects.get_or_create.return_value = (mock_site, True)
            mock_social_app_class.objects.get_or_create.return_value = (mock_social_app, True)

            configure_social_apps(sender=mock_sender)

            # Verify Site creation
            mock_site_class.objects.get_or_create.assert_called_once()

            # Verify SocialApp creation
            mock_social_app_class.objects.get_or_create.assert_called_once_with(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': 'test_client_id',
                    'secret': 'test_client_secret',
                }
            )

            # Verify site is added to social app
            mock_social_app.sites.add.assert_called_once_with(mock_site)

            # Verify success message is printed
            mock_print.assert_any_call('Created Google SocialApp')
            mock_print.assert_any_call('SocialApp configuration completed')

    @pytest.mark.timeout(30)
    @patch('django_app.signals.SOCIAL_LOGIN_PROVIDERS', {
        'google': {
            'name': 'Google',
            'client_id': None,
            'client_secret': 'test_client_secret'
        }
    })
    def test_skips_provider_with_missing_client_id(self):
        """Test that provider is skipped when client_id is missing."""
        mock_sender = MagicMock()
        mock_sender.name = "django_app"

        mock_site = MagicMock()

        with patch('django_app.signals.Site') as mock_site_class, \
             patch('django_app.signals.SocialApp') as mock_social_app_class, \
             patch('builtins.print') as mock_print:

            mock_site_class.objects.get_or_create.return_value = (mock_site, True)

            configure_social_apps(sender=mock_sender)

            # Verify SocialApp creation was not attempted
            mock_social_app_class.objects.get_or_create.assert_not_called()

            # Verify skip message is printed
            mock_print.assert_any_call('Skipping Google - credentials not provided')

    @pytest.mark.timeout(30)
    @patch('django_app.signals.SOCIAL_LOGIN_PROVIDERS', {
        'google': {
            'name': 'Google',
            'client_id': 'test_client_id',
            'client_secret': None
        }
    })
    def test_skips_provider_with_missing_client_secret(self):
        """Test that provider is skipped when client_secret is missing."""
        mock_sender = MagicMock()
        mock_sender.name = "django_app"

        mock_site = MagicMock()

        with patch('django_app.signals.Site') as mock_site_class, \
             patch('django_app.signals.SocialApp') as mock_social_app_class, \
             patch('builtins.print') as mock_print:

            mock_site_class.objects.get_or_create.return_value = (mock_site, True)

            configure_social_apps(sender=mock_sender)

            # Verify SocialApp creation was not attempted
            mock_social_app_class.objects.get_or_create.assert_not_called()

            # Verify skip message is printed
            mock_print.assert_any_call('Skipping Google - credentials not provided')

    @pytest.mark.timeout(30)
    @patch('django_app.signals.SOCIAL_LOGIN_PROVIDERS', {
        'google': {
            'name': 'Google',
            'client_id': 'your_google_client_id',
            'client_secret': 'your_google_client_secret'
        }
    })
    def test_skips_provider_with_placeholder_credentials(self):
        """Test that provider is skipped when placeholder credentials are detected."""
        mock_sender = MagicMock()
        mock_sender.name = "django_app"

        mock_site = MagicMock()

        with patch('django_app.signals.Site') as mock_site_class, \
             patch('django_app.signals.SocialApp') as mock_social_app_class, \
             patch('builtins.print') as mock_print:

            mock_site_class.objects.get_or_create.return_value = (mock_site, True)

            configure_social_apps(sender=mock_sender)

            # Verify SocialApp creation was not attempted
            mock_social_app_class.objects.get_or_create.assert_not_called()

            # Verify skip message is printed
            mock_print.assert_any_call('Skipping Google - placeholder credentials detected')

    @pytest.mark.timeout(30)
    @patch('django_app.signals.SOCIAL_LOGIN_PROVIDERS', {
        'google': {
            'name': 'Google Updated',
            'client_id': 'updated_client_id',
            'client_secret': 'updated_client_secret'
        }
    })
    def test_updates_existing_social_app(self):
        """Test that existing SocialApp is updated with new credentials."""
        mock_sender = MagicMock()
        mock_sender.name = "django_app"

        mock_site = MagicMock()
        mock_social_app = MagicMock()
        mock_social_app.sites = MagicMock()

        with patch('django_app.signals.Site') as mock_site_class, \
             patch('django_app.signals.SocialApp') as mock_social_app_class, \
             patch('builtins.print') as mock_print:

            mock_site_class.objects.get_or_create.return_value = (mock_site, True)
            # Return created=False to simulate existing app
            mock_social_app_class.objects.get_or_create.return_value = (mock_social_app, False)

            configure_social_apps(sender=mock_sender)

            # Verify SocialApp fields are updated
            self.assertEqual(mock_social_app.name, 'Google Updated')
            self.assertEqual(mock_social_app.client_id, 'updated_client_id')
            self.assertEqual(mock_social_app.secret, 'updated_client_secret')

            # Verify save is called
            mock_social_app.save.assert_called_once()

            # Verify site is added
            mock_social_app.sites.add.assert_called_once_with(mock_site)

            # Verify update message is printed
            mock_print.assert_any_call('Updated Google Updated SocialApp')