from django.core.management.base import BaseCommand
from app1.models import User, Punch
from datetime import date, datetime
from app1.utils import parse_and_format_date

class Command(BaseCommand):
    help = 'Delete Unmatched Punch Records'
    def add_arguments(self, parser):
            # Optional: Define command-line arguments
            parser.add_argument('date_str', type=str, help='The date to process in YYYY-MM-DD format (e.g., 2025-03-02)')

    def handle(self, *args, **options):
        """date should be given in YYYY-MM-DD"""

        try:
            specific_date = datetime.strptime(options['date_str'], '%Y-%m-%d').date()
            employees = User.objects.filter(status='Active').prefetch_related(
            'punch_set', 'leave_set', 'assignattendancerule_set',)
            for employee in employees:
                if employee.datejoin:
                    join_date_str = employee.datejoin.strip()  # Remove potential leading/trailing whitespace
                    employee_join_date = datetime.strptime(join_date_str, '%d %B %Y').date()
                    # print(employee_join_date)
                    # print(specific_date)
                    if employee_join_date > specific_date:
                        print(employee_join_date)
                        print(specific_date)
                        print(employee.username)
                        punch_to_delete = Punch.objects.filter(user=employee, date=specific_date, status='WO', is_first_clocked_in=True, is_first_clocked_out=True, last_punch_type=2)
                        punch_to_delete.delete()
            return 'Success'
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to process data: {e}'))