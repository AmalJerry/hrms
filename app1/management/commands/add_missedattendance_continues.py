from django.core.management.base import BaseCommand
from datetime import datetime, timedelta, time
from app1.models import User, Punch  # Replace 'your_app' with your actual app name

class Command(BaseCommand):
    help = 'Add missed attendance for an employee for a date range using email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Employee email address')
        parser.add_argument('start_date', type=str, help='Start date (YYYY-MM-DD)')
        parser.add_argument('end_date', type=str, help='End date (YYYY-MM-DD)')

    def handle(self, *args, **options):
        email = options['email']
        start_date_str = options['start_date']
        end_date_str = options['end_date']

        try:
            # Convert date strings to datetime objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()

            # Validate date range
            if start_date > end_date:
                self.stdout.write(self.style.ERROR("Start date must be before or equal to end date"))
                return

            # Get the employee by email
            employee = User.objects.get(email=email)
            if not employee:
                self.stdout.write(self.style.ERROR(f"No employee found with email {email}"))
                return

            # Default shift times
            in_time = time(9, 30)  # 9:30 AM
            out_time = time(18, 30)  # 6:30 PM
            work_duration = time(9, 0)  # 9 hours

            # Iterate through the date range
            current_date = start_date
            while current_date <= end_date:
                # Check if a Punch record already exists for the date
                existing_punch = Punch.objects.filter(
                    user=employee, date__date=current_date
                ).exists()

                if not existing_punch:
                    # Create a new Punch record with naive datetime
                    punch = Punch(
                        user=employee,
                        first_clock_in_time=in_time,
                        first_clock_out_time=out_time,
                        is_first_clocked_in=True,
                        is_first_clocked_out=True,
                        work_duration=work_duration,
                        punch_in_count=1,
                        punch_out_count=1,
                        date=datetime.combine(current_date, time(0, 0)),  # Naive datetime
                        status="P",  # Present
                        ip_address="103.160.233.183",  # Default IP OF AMRUTHA TS CHANGE ACCORDINGLY
                        location="WFH",  # Default location
                        break_duration=time(0, 0),  # No break
                        overtime=time(0, 0),  # No overtime
                        break_count=0,
                        last_punch_type=1,
                        is_shift_one=True,
                        is_shift_two=False,
                        in_time_anomaly=False,
                        out_time_anomaly=False,
                        work_duration_anomaly=False,
                        is_week_work=False,
                        is_holiday_work=False,
                        is_requested=False,
                        is_approved=False,
                        is_rejected=False,
                        is_penalty=False,
                        is_penalty_reverted=False,
                        is_compoff_reverted=False,
                        WfhOrWfo="WFO"  # Work From Office
                    )
                    punch.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"Added attendance for {employee.email} on {current_date}"
                    ))
                else:
                    self.stdout.write(
                        f"Attendance already exists for {employee.email} on {current_date}"
                    )

                # Move to the next date
                current_date += timedelta(days=1)

            self.stdout.write(self.style.SUCCESS(
                f"Successfully added attendance for {employee.email} from {start_date} to {end_date}"
            ))

        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"No employee found with email {email}"))
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f"Invalid date format: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An error occurred: {e}"))





