from decimal import Decimal, getcontext
from app1.models import *
from django.db.models import Q
from django.db.models import Sum
import calendar
import datetime
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Case, IntegerField, When
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse
from django.core.mail import EmailMultiAlternatives

# Notifications for employee birthday and work anniversary before 15 days

def notification_employee():
    today = datetime.now().date()
    fifteen_days_from_now = today + timedelta(days=14)
    print("fifteen_days_from_now :", fifteen_days_from_now)

    users = User.objects.filter(dob__isnull=False)

    for user in users:
        dob_date = datetime.strptime(user.dob, '%d %B %Y').date()

        if dob_date.month == fifteen_days_from_now.month and dob_date.day == fifteen_days_from_now.day:
            message = f"{user.username}'s birthday is coming up in 15 days."
            LeaveNotification.objects.create(user=user, message=message, events=1)

    users_anniversaries = User.objects.filter(datejoin__isnull=False )

    for user in users_anniversaries:
        doj_date = datetime.strptime(user.datejoin, '%d %B %Y').date()

        if doj_date.month == fifteen_days_from_now.month and doj_date.day == fifteen_days_from_now.day and doj_date.year != today.year:
            message = f"{user.username}'s work anniversary is coming up in 15 days."
            LeaveNotification.objects.create(user=user, message=message, events=2)
    return HttpResponse("SUCCESS")
