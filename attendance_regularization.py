import datetime
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from app1.models import User, companyprofile, Punch
from django.db.models import Count, Q


def att_regularization():
    today = date.today()
    if today.day == 24:
        anomalies = Punch.objects.filter(date__month=today.month,date__year=today.year,status='AN')

        anomalies_per_user = anomalies.values('user').annotate(num_anomalies=Count('id'))

        for anomaly_info in anomalies_per_user:
            user_id = anomaly_info['user']
            num_anomalies = anomaly_info['num_anomalies']
            user_anomalies = anomalies.filter(user=user_id)
            
            if num_anomalies >= 1 and num_anomalies == user_anomalies.count():
                user = User.objects.get(id=user_id)

                companydatas = companyprofile.objects.filter(Q(admin_id=user.admin_id) | Q(admin_id=user.id)).first()

                to = [user.email]
                subject = "Attendance Regularization Reminder"
                html_body = render_to_string('index/att_regularization.html', {'user': user, 'companydatas':companydatas})
                msg = EmailMultiAlternatives(subject=subject, from_email=settings.EMAIL_HOST_USER, to=to)
                msg.attach_alternative(html_body, "text/html")
                msg.send()
    return HttpResponse("SUCCESS")
