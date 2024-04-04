# In delete_expired_pending_users.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import PendingUser

class Command(BaseCommand):
    help = 'Deletes expired pending users'

    def handle(self, *args, **options):
        # Get current date and time
        current_time = timezone.now()
        
        # Delete expired pending users
        expired_users = PendingUser.objects.filter(expiry_time__lt=current_time)
        expired_users.delete()

        self.stdout.write(self.style.SUCCESS('Expired pending users deleted successfully.'))
