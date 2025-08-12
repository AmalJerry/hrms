from django.core.management.base import BaseCommand
from app1.models import User, Punch
from datetime import date, datetime

class Command(BaseCommand):
    help = 'Update missed attendance based on day'
    def add_arguments(self, parser):
            # Optional: Define command-line arguments
            parser.add_argument('date_str', type=str, help='The date to process in YYYY-MM-DD format (e.g., 2025-03-02)')

    def handle(self, *args, **options):
        """date should be given in YYYY-MM-DD"""

        try:
            date_to_add = datetime.strptime(options['date_str'], '%Y-%m-%d').date()
            print(date_to_add)
            employees = User.objects.filter(status='Active').prefetch_related(
            'punch_set', 'leave_set', 'assignattendancerule_set',)
            for employee in employees:
                Punch.objects.get_or_create(user=employee, date=date_to_add, status='WO', is_first_clocked_in=True, is_first_clocked_out=True, last_punch_type=2)
            return 'Success'
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to process data: {e}'))