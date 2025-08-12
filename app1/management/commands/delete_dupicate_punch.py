from django.core.management.base import BaseCommand
from app1.models import User, Punch
from datetime import date, datetime
from app1.utils import parse_and_format_date
from django.db.models import Q

class Command(BaseCommand):
    help = 'Delete Unmatched Punch Records'
    def add_arguments(self, parser):
            # Optional: Define command-line arguments
            parser.add_argument('date_str', type=str, help='The date to process in YYYY-MM-DD format (e.g., 2025-03-02)')

    def handle(self, *args, **options):
        """date should be given in YYYY-MM-DD"""

        try:
            specific_date = datetime.strptime(options['date_str'], '%Y-%m-%d').date()
            selectedday = specific_date.day
            selectedmonth = specific_date.strftime("%B")
            selectedyear = specific_date.year
            print(selectedday,selectedmonth,selectedyear)
            employees = User.objects.filter(status='Active').prefetch_related(
            'punch_set', 'leave_set', 'assignattendancerule_set',)
            
            duplicate_punch_query = []
            to_delete_id = []

            for employee in employees:
                punches_in_today = Punch.objects.filter(
                    Q(date=specific_date) &
                    (Q(user__id=employee.id) | Q(user__admin_id=employee.id))
                )
                # if employee.id == 112:
                #      print('punches_in_today',punches_in_today)
                if punches_in_today.count() > 1:
                     punches_in_today.last().delete()
            #         to_keep = punches_in_today.first()
            #         to_delete_ids = [p.id for p in punches_in_today if p.id != to_keep.id]

            #         print(f"{employee.username} KEEP: {to_keep.id}")
            #         print(f"{employee.username} DELETE: {to_delete_ids}")

            #         to_delete_id.extend(to_delete_ids)
            #     # unique_user_ids = []
            #     # for punch in punches_in_today:
            #     #     if employee.id in unique_user_ids:
            #     #      duplicate_punch_query.append(punch)
            #     #     else:
            #     #         unique_user_ids.append(employee.id)
            # # print(duplicate_punch_query)
            #     # join_date_str = employee.datejoin.strip()  # Remove potential leading/trailing whitespace
            #     # employee_join_date = datetime.strptime(join_date_str, '%d %B %Y').date()
            #     # print(employee_join_date)
            #     # print(specific_date)
            #     # if employee_join_date > specific_date:
            #     #     print(employee_join_date)
            #     #     print(specific_date)
            #     #     print(employee.username)
            #     #     punch_to_delete = Punch.objects.filter(user=employee, date=specific_date, status='WO', is_first_clocked_in=True, is_first_clocked_out=True, last_punch_type=2)
            #     #     punch_to_delete.delete()
            # print('to_delete_id',to_delete_id)
            # if to_delete_id:
            #     Punch.objects.filter(id__in=to_delete_id).delete()
            return 'Success'
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to process data: {e}'))