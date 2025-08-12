import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from app1.models import User,companyprofile
from django.template.loader import render_to_string

def birthdaymail():
    today = date.today()
    formatted_today = today.strftime("%d %B")

    employees = User.objects.filter(role="Employee")
    
    for employee in employees:
        dateofbirth_str=employee.dob
        formatted_dateofbirth=None

        if dateofbirth_str:
            try:
                dateofbirth = datetime.strptime(dateofbirth_str, "%d %B %Y").date()
                formatted_dateofbirth = dateofbirth.strftime("%d %B")
                print(f"Formatted datejoin for employee {employee.username} : {formatted_dateofbirth}")
            except ValueError as e:
                pass
        else:
            pass

        if formatted_dateofbirth == formatted_today:
            Age=relativedelta(today, dateofbirth).years            
            admin = User.objects.filter(role="Admin", id=employee.admin_id).first()
            
            
            to = [admin.email]
            subject = f"Today is {employee.username}'s  Birthday!"
            html_body = render_to_string('index/birthdaymail.html', {'employee': employee, 'admin':admin,'Age':Age,  'formatted_today':  formatted_today })
            msg = EmailMultiAlternatives(subject=subject, from_email=settings.EMAIL_HOST_USER, to=to)
            msg.attach_alternative(html_body, "text/html")
            msg.send()
            print("SUCCESS")
    return HttpResponse("SUCCESS")
