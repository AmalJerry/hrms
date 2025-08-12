from django.core.management.base import BaseCommand
from django.db.models import Count, Min
from django.db.models.functions import TruncDate
from app1.models import Punch, User  # Replace 'your_app' with your actual app name
from datetime import datetime

class Command(BaseCommand):
    help = 'Deletes duplicate punch records for a specific user on a specific date, keeping the earliest.'

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int, help='User ID to process')
        parser.add_argument('date', type=str, help='Date to process (YYYY-MM-DD)')

    def handle(self, *args, **options):
        user_id = options['user_id']
        date_str = options['date']

        # Validate user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with ID {user_id} does not exist"))
            return

        # Validate date
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            self.stdout.write(self.style.ERROR(f"Invalid date format: {date_str}. Use YYYY-MM-DD"))
            return

        self.stdout.write(f"Processing duplicates for user: {user.email} on date: {target_date}")

        # Find duplicate punch records for the user on the specific date
        duplicates = (
            Punch.objects
            .filter(user=user, date__date=target_date)
            .values('user', 'date__date')
            .annotate(count=Count('id'), min_id=Min('id'))
            .filter(count__gt=1)
        )

        if not duplicates:
            self.stdout.write(self.style.SUCCESS(f"No duplicates found for user: {user.email} on date: {target_date}"))
            return

        # Delete duplicates, keeping the record with the minimum ID
        deleted = (
            Punch.objects
            .filter(user=user, date__date=target_date)
            .exclude(id=duplicates[0]['min_id'])
            .delete()
        )
        deleted_count = deleted[0]

        self.stdout.write(self.style.SUCCESS(
            f"Deleted {deleted_count} duplicate punch record(s) for user: {user.email} on date: {target_date}"
        ))