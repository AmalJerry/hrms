# management/commands/send_birthday_reminders.py

import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from app1.models import User

class Command(BaseCommand):
    help = 'Send birthday reminder emails to admin'

    def handle(self, *args, **kwargs):
        # Get the current date
        today = datetime.date.today()
        today_formatted = today.strftime("%d %B %Y")

        # Get employees whose birthday is today
        employees = User.objects.filter(role='Employee', dob=today_formatted)
        admin = User.objects.filter(role='Admin')

        # Send emails to the admin for each employee
        if employees:
            subject = 'Birthday Reminder'
            message = 'Today is the birthday of the following employees:\n'
            for employee in employees:
                message += f'- {employee.get_username()}\n'
            admin_emails = [admin.email for admin in admin]

            send_mail(subject, message, settings.EMAIL_HOST_USER, admin_emails, fail_silently=False)
            print('Birthday reminder emails sent successfully!')
        else:
            print('No employee birthdays today. No email sent.')

