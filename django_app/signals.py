"""
Django signals for configuring OAuth providers from environment variables.

Important points:
- we use django-allauth library to implement social logins
- social login is configured via DB-stored SocialApp instances, not settings.py or migrations
- list of providers is defined in SOCIAL_LOGIN_PROVIDERS dictionary
- env variables are read via _read_config_parameter function, keys come from external APIs analysis
"""

import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from dotenv import dotenv_values
from pathlib import Path


def _read_config_parameter(param_name: str) -> str | None:
    """
    Read a configuration parameter from the .env.local file without mutating the current environment.
    Note that it's important that the function reads the parameter from the .env.local file first,
    and then from the environment variables.
    Case-insensitive.
    """
    param_name = param_name.upper()
    file = Path(".env.local")
    env_map = dotenv_values(file) if file.exists() else {}
    value_from_env_local = env_map.get(param_name)
    value_from_env = os.getenv(param_name)
    return value_from_env_local or value_from_env or None

# Configuration for social login providers
#
# SOCIAL_LOGIN_PROVIDERS Structure:
# ================================
#
# This dictionary defines OAuth provider configurations for Django AllAuth.
# Each provider entry contains the following structure:
#
# {
#     "provider_id": {
#         "name": str,          # Display name for the provider (shown in admin)
#         "client_id": str,     # OAuth client ID from environment variables
#         "client_secret": str, # OAuth client secret from environment variables
#     }
# }
#
# Provider IDs must match Django AllAuth provider identifiers:
# - "google" -> Google OAuth 2.0
# - "microsoft" -> Microsoft OAuth 2.0
# - "github" -> GitHub OAuth 2.0
# - "amazon" -> Amazon OAuth 2.0
# - "openid_connect" -> Generic OpenID Connect (for LinkedIn, etc.)
# - "slack" -> Slack OAuth 2.0
# - "spotify" -> Spotify OAuth 2.0
# - "facebook" -> Facebook OAuth 2.0
# - "twitter" -> Twitter OAuth 2.0
# - "discord" -> Discord OAuth 2.0
# - And many more (see allauth.socialaccount.providers)
#
# "client_id" and "client_secret" MUST be read by _read_config_parameter() function,
# as it correctly handles different sources of config parameters.
#
#
# Note: For OpenID Connect providers (like LinkedIn), you may need to configure
# additional settings in the Django admin or via environment variables:
# - OPENID_CONNECT_ISSUER_URL (e.g., https://www.linkedin.com/oauth/v2/authorization)
# - OPENID_CONNECT_SCOPE (e.g., openid profile email)
SOCIAL_LOGIN_PROVIDERS = {
    "google": {
        "name": "Google",
        "client_id": _read_config_parameter("GOOGLE_OAUTH_CLIENT_ID"),
        "client_secret": _read_config_parameter("GOOGLE_OAUTH_CLIENT_SECRET"),
    },
    # Add more providers as needed...
}

@receiver(post_migrate)
def configure_social_apps(sender, **kwargs):
    """
    Configure SocialApps in the database after migrations.
    This signal reads OAuth provider credentials from environment variables
    and creates/updates SocialApp instances in the database.
    """
    # Only run this for the django_app app
    if sender.name != "django_app":
        return

    # Get the default site
    site, _ = Site.objects.get_or_create(
        id=os.getenv("SITE_ID", 1),
        defaults={"domain": "localhost:8000", "name": "Bloggo"},
    )

    # Create or update SocialApp instances
    for provider_id, config in SOCIAL_LOGIN_PROVIDERS.items():
        # Skip if credentials are not provided
        if not config["client_id"] or not config["client_secret"]:
            print(f"Skipping {config['name']} - credentials not provided")
            continue

        # Skip if credentials are placeholder values
        if config["client_id"].startswith("your_") or config[
            "client_secret"
        ].startswith("your_"):
            print(f"Skipping {config['name']} - placeholder credentials detected")
            continue

        # Create or update the SocialApp
        social_app, created = SocialApp.objects.get_or_create(
            provider=provider_id,
            defaults={
                "name": config["name"],
                "client_id": config["client_id"],
                "secret": config["client_secret"],
            },
        )

        if not created:
            # Update existing app
            social_app.name = config["name"]
            social_app.client_id = config["client_id"]
            social_app.secret = config["client_secret"]
            social_app.save()

        # Add the site to the social app
        social_app.sites.add(site)

        print(f"{'Created' if created else 'Updated'} {config['name']} SocialApp")

    print("SocialApp configuration completed")