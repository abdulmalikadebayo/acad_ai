import re

from django.db import transaction

from djp import settings
from supabase import Client, create_client

from .models import Profile, User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def norm_email(s: str) -> str:
    return (s or "").strip().lower()


def get_or_create_local_user(email: str, country: str | None = None):
    with transaction.atomic():
        user, created = User.objects.get_or_create(
            username=email,
            defaults={"email": email},
        )
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.save()
        return user, profile, created


def supabase_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)


def supabase_admin_client() -> Client:
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
