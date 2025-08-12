from django.core.management.base import BaseCommand
from app1.models import User, Punch
from datetime import datetime

class Command(BaseCommand):
    help = 'Remove a specific user\'s attendance record for a specific date'

    def add_arguments(self, parser):
        parser.add_argument('user_email', type=str, help='Email of the user')
        parser.add_argument('date_str', type=str, help='Date of the record to remove (YYYY-MM-DD)')

    def handle(self, *args, **options):
        user_email = options['user_email']
        date_str = options['date_str']

        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            self.stderr.write(self.style.ERROR('Invalid date format. Use YYYY-MM-DD.'))
            return

        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'User with email {user_email} does not exist.'))
            return

        deleted, _ = Punch.objects.filter(user=user, date=target_date).delete()

        if deleted:
            self.stdout.write(self.style.SUCCESS(
                f'Successfully removed attendance for {user.email} on {target_date}'
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f'No attendance found for {user.email} on {target_date}'
            ))
