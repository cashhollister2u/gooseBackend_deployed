import django
import os
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gooseProject.settings")  # Replace with your project's settings
django.setup()

from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

def delete_expired_tokens():
    # Get the current time
    now = timezone.now()

    # Find all tokens that have expired
    expired_tokens = OutstandingToken.objects.filter(expires_at__lt=now)

    # Count them for logging
    count = expired_tokens.count()

    # Delete the expired tokens
    expired_tokens.delete()

    print(f"Deleted {count} expired tokens")

if __name__ == "__main__":
    delete_expired_tokens()