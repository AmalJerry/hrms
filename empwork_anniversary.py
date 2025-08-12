import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from app1.models import User, companyprofile

# WORK ANNIVERSARY MAIL SEND TO EMPLOYEES

def emp_work_anniversary():
    today = date.today()
    formatted_today = today.strftime("%d %B")

    employees = User.objects.filter(status__in=['Active', 'Onboarding'])
    for employee in employees:
        datejoin_str = employee.datejoin
        formatted_datejoin = None
        dateofjoin = None
    
        if datejoin_str:
            try:    
                dateofjoin = datetime.strptime(datejoin_str, "%d %B %Y").date()
                formatted_datejoin = dateofjoin.strftime("%d %B")
            except ValueError as e:
                pass
        else:
            pass

        years_of_service = relativedelta(today, dateofjoin).years

        if formatted_datejoin == formatted_today and years_of_service >= 1 :

            admin_id = User.objects.filter(id=employee.admin_id).first()

            companydatas = companyprofile.objects.filter(admin_id=employee.admin_id).first()

            to = [employee.email]
            subject = f'Celebrating {years_of_service} Years of Dedication and Excellence!'
            html_body = render_to_string('index/email_empworkanniversary.html', {'employee': employee, 'adminid':admin_id, 'years_of_service': years_of_service, 'companydetail': companydatas})
            msg = EmailMultiAlternatives(subject=subject, from_email=settings.EMAIL_HOST_USER, to=to)
            msg.attach_alternative(html_body, "text/html")
            msg.send()
            print("SUCCESS")
    return HttpResponse("SUCCESS")
