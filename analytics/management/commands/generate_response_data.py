# analytics/management/commands/generate_response_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
import random
import uuid
from users.models import CustomUser
from presence.models import Presence
from analytics.models import ResponseHistory

class Command(BaseCommand):
    help = 'Generate fake response history data for users'

    def add_arguments(self, parser):
        parser.add_argument('--user-id', type=str, help='UUID of the user to generate data for')

    def handle(self, *args, **options):
        user_id = options['user_id']
        if not user_id:
            self.stdout.write(self.style.ERROR('Please provide a user ID using --user-id'))
            return

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User with ID {user_id} not found'))
            return

        # Get the user's current presence status
        presence, created = Presence.objects.get_or_create(user=user)

        # Generate 10 fake response records
        for _ in range(10):
            # Simulate a message received within the last 30 days
            days_ago = random.randint(1, 30)
            hours_ago = random.randint(0, 23)
            minutes_ago = random.randint(0, 59)
            received_at = timezone.now() - timezone.timedelta(
                days=days_ago, hours=hours_ago, minutes=minutes_ago
            )

            # Simulate response time (between 1 minute and 2 hours)
            response_delay = random.randint(60, 7200)  # Seconds (1 min to 2 hours)
            responded_at = received_at + timezone.timedelta(seconds=response_delay)

            # Simulate presence status at the time of response
            possible_statuses = ['online', 'offline', 'away', 'busy']
            simulated_status = random.choice(possible_statuses)

            ResponseHistory.objects.create(
                user=user,
                message_id=str(uuid.uuid4()),
                received_at=received_at,
                responded_at=responded_at,
                presence_status=simulated_status,
                response_time=response_delay
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully generated 10 response history records for user {user.email}'))