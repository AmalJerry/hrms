import arrow
from .models import CompanyRules, Punch, assignrule, AssignWorkWeek, HolidayList, HolidayLocationList, Leave  # User,CompOff,
from django.utils import timezone
from datetime import datetime, timedelta, time
from calendar import monthcalendar

from django.db.models import Q

"""
Time Delta Converter
"""


def timedelta_from_datetime_or_time(input_time):
    if isinstance(input_time, datetime):
        return datetime.now() - input_time
    elif isinstance(input_time, time):
        # Constructing timedelta directly from input time
        return timedelta(hours=input_time.hour, minutes=input_time.minute, seconds=input_time.second, microseconds=input_time.microsecond)
    elif isinstance(input_time, timedelta):
        return input_time
    else:
        print("Input must be either datetime.datetime or datetime.time")


"""
Get Off Day's Data
"""


def get_weekly_off_day(employee):
    current_time = timezone.now()
    work_week_records = None
    try:
        work_week_records = AssignWorkWeek.objects.get(user_id=employee)
    except AssignWorkWeek.DoesNotExist:
        work_week_records = None

    if work_week_records:
        date_data = monthcalendar(current_time.year, current_time.month)
        day_fields = [f"day_{day}" for day in range(1, 36)]
        for day_index, day in enumerate([day for week in date_data for day in week]):
            day_field_index = day_index % 35
            day_field = day_fields[day_field_index]

            if day == current_time.day:
                return getattr(work_week_records.rules_applied, day_field)
                # return True
    else:
        return "#28a745"
        # return False


def get_holiday(employee, previous_rules, is_anomaly, holiday_list, comp_off_rule, now, org_in_time_minutes, combine_in_time_minute):
    current_time = now.time().replace(microsecond=0)
    # current_time_minutes = (current_time.hour, current_time.minute)
    for holiday in holiday_list:
        holiday_location = HolidayLocationList.objects.filter(
            Q(Holiday_List=holiday))
        for location in holiday_location:
            work_location = location.HolidayLocation.first().location
            is_optional = location.HolidayToggleBtn_ON
            if employee.wrklcn and employee.wrklcn.location == work_location and is_optional == 'off':
                # if current_time_minutes > org_in_time_minutes and current_time_minutes > combine_in_time_minute and is_anomaly:
                #     status = "AN"
                # else:
                #     status = 'P'
                # punch_data = Punch.objects.create(
                #     user=employee,
                #     first_clock_in_time=current_time,
                #     is_first_clocked_in=True,
                #     punch_in_count=1,
                #     is_shift_one=True,
                #     date=now.date(),
                #     last_punch_type=1,
                #     status=status,
                #     is_holiday_work=True,
                # )
                # if punch_data.status == 'AN':
                #     punch_data.in_time_anomaly = True
                #     punch_data.save()
                return True

        return False


def get_half_day_leave(leave_data):
    if leave_data.Selecthalf1 == "first half" and leave_data.Selecthalf2 == "first half":
        return "first half"
    elif leave_data.Selecthalf1 == "second half" and leave_data.Selecthalf2 == "second half":
        return "second half"


def get_leave_data(employee, now):

    leave_data = employee.leave_set.filter(
        strtDate__lte=now.date(), endDate__gte=now.date(),
        Appliedon__lte=now.date(), status='Approved'
    ).order_by('-strtDate').first()
    if leave_data and leave_data.Days == 0.5:
        return get_half_day_leave(leave_data)
    if leave_data and leave_data.Days > 1:
        if leave_data.Selecthalf1 == leave_data.Selecthalf2:
            return get_half_day_leave(leave_data)
        if leave_data.strtDate == now.date() and '.5' in str(leave_data.Days):
            return get_half_day_leave(leave_data)


"""
Time Duration find funcions
"""


def get_full_hour(full_hour, full_minutes):

    full_day = timedelta(minutes=full_hour * 60 + full_minutes)
    return full_day


def get_half_hour(half_hour, half_minutes):
    half_day = timedelta(minutes=half_hour * 60 + half_minutes)
    return half_day


def combined_in_time(org_in_time, in_grace_period):
    # Convert time objects to datetime objects with a common date
    datetime1 = datetime.combine(datetime.min, org_in_time)
    datetime2 = datetime.combine(datetime.min, in_grace_period)

    # Calculate the time difference between datetime2 and the minimum datetime
    time_difference = datetime2 - datetime.min

    # Add the timedelta to datetime1
    result_datetime = datetime1 + time_difference
    print("result_datetime :", result_datetime)

    # Extract the time from the resulting datetime object
    return result_datetime.time()


def get_break_start_time(org_in_time, org_out_time, attendance_rule):

    full_hour = get_full_hour(
        attendance_rule.rules_applied.fullhours, attendance_rule.rules_applied.fullminutes)
    half_hour = get_half_hour(
        attendance_rule.rules_applied.halfhours, attendance_rule.rules_applied.halfminutes)
    org_work_duration = arrow.get(
        str(org_out_time), "HH:mm:ss") - arrow.get(str(org_in_time), "HH:mm:ss")

    difference_between_org_time_duraion_and_inTime_outTime_duraion = org_work_duration - full_hour
    if not difference_between_org_time_duraion_and_inTime_outTime_duraion < full_hour:
        break_start_time = datetime.combine(
            datetime.today(), org_in_time) + half_hour
        return break_start_time.time()


def get_break_end_time(org_in_time, org_out_time, attendance_rule):

    full_hour = get_full_hour(
        attendance_rule.rules_applied.fullhours, attendance_rule.rules_applied.fullminutes)
    # half_hour = get_half_hour(
    #     attendance_rule.rules_applied.halfhours, attendance_rule.rules_applied.halfminutes)
    org_work_duration = arrow.get(
        str(org_out_time), "HH:mm:ss") - arrow.get(str(org_in_time), "HH:mm:ss")

    difference_between_org_time_duraion_and_inTime_outTime_duraion = org_work_duration - full_hour
    if not difference_between_org_time_duraion_and_inTime_outTime_duraion < full_hour:
        break_end_time = datetime.combine(
            datetime.today(), org_in_time) + difference_between_org_time_duraion_and_inTime_outTime_duraion
        return break_end_time.time()
    else:
        return time(hour=0, minute=0, second=0)


# start point

def clocked_in(request, employee, punch_object, attendance_rule, location):
    now = datetime.now()
    clock_in_flag = False    

    IP_address= request.META.get("REMOTE_ADDR")
    print("Employee ======> ", employee, now.time().replace(microsecond=0))

    # Time variable in Attendance Rule
    current_time = now.time().replace(microsecond=0)
    in_grace_period = getattr(attendance_rule.rules_applied, "inGracePeriod", now.time(
    )) if attendance_rule else now.time()
    # out_grace_period = getattr(attendance_rule.rules_applied, "outGracePeriod", now.time(
    # )) if attendance_rule else now.time()
    org_in_time = getattr(attendance_rule.rules_applied, "inTime")
    org_out_time = getattr(attendance_rule.rules_applied, "outTime")
    combine_in_time = combined_in_time(org_in_time, in_grace_period)

    # Getting Half hour duration
    half_hour = get_half_hour(
        attendance_rule.rules_applied.halfhours, attendance_rule.rules_applied.halfminutes)

    # tupled times for condition
    current_time_minutes = (current_time.hour, current_time.minute)
    org_in_time_minutes = (org_in_time.hour, org_in_time.minute)
    combine_in_time_minute = (combine_in_time.hour, combine_in_time.minute)

    # Rule Varibales in Attendance Rule
    is_anomaly = getattr(attendance_rule.rules_applied, "enable_AT", False)
    is_comp_off = getattr(attendance_rule.rules_applied, "enable_CO", False)
    comp_off_rule = CompanyRules.objects.filter(
        admin_id__in=[employee.id, employee.admin_id], leavename='Comp Off').first()

    previous_rules = assignrule.objects.filter(
        user_id=employee, rules_applied__id=comp_off_rule.id).first()

    # Get weeklyLoff day / Holiday
    checking_holiday = False  # Checking today is holiday
    holiday_list = HolidayList.objects.filter(
        Q(Myuser_13__in=[employee.id, employee.admin_id]),
        HolidayDate=now.date().strftime('%d %B %Y'))
    if holiday_list:
        checking_holiday = get_holiday(employee, previous_rules, is_anomaly,
                                       holiday_list, comp_off_rule, now, org_in_time_minutes, combine_in_time_minute)
    is_weekly_off = get_weekly_off_day(employee)

    half_leave_data = get_leave_data(employee, now)

    # if user Apply any leave(Second Half)
    # break_start_time = get_break_start_time(
    #     org_in_time, org_out_time, attendance_rule)

    break_end_time = get_break_end_time(org_in_time, org_out_time, attendance_rule)

    if break_end_time.hour == 0 and break_end_time.minute == 0:
        combined_second_in_time = datetime.strptime(str((timedelta_from_datetime_or_time(
            org_out_time) - timedelta_from_datetime_or_time(half_hour)) + timedelta_from_datetime_or_time(in_grace_period)), "%H:%M:%S")
        print("combined_second_in_time 1 : ", combined_second_in_time)
    else:
        combined_second_in_time = datetime.strptime(str(timedelta_from_datetime_or_time(in_grace_period) + timedelta_from_datetime_or_time(break_end_time)), "%H:%M:%S")
        print("combined_second_in_time 2 : ", combined_second_in_time)
    # second clock in time after a break
    combined_second_in_time_minutes = (combined_second_in_time.hour, combined_second_in_time.minute)

    print("current_time_minutes, combined_second_in_time_minutes:", current_time_minutes, combined_second_in_time_minutes)

    # print("Cheking holiday and week day", checking_holiday, is_weekly_off)
    # print("---------------------------------------------------------------")
    if half_leave_data == "first half":

        if current_time_minutes > combined_second_in_time_minutes:
            Punch.objects.create(
                user=employee,
                WfhOrWfo=location,
                first_clock_in_time=current_time,
                is_first_clocked_in=True,
                punch_in_count=1,
                is_shift_one=True,
                last_punch_type=1,
                status='AN',
                in_time_anomaly=True,
                ip_address= IP_address,
                date=now.date()
            )
            clock_in_flag = True
            # print("Today is first half leave and anomaly")
        else:
            Punch.objects.create(
                user=employee,
                WfhOrWfo=location,
                first_clock_in_time=current_time,
                is_first_clocked_in=True,
                punch_in_count=1,
                is_shift_one=True,
                last_punch_type=1,
                status='HL',
                ip_address=IP_address,
                date=now.date()
            )
            clock_in_flag = True
            # print("Today is first half leave and present")

    elif current_time_minutes > org_in_time_minutes and current_time_minutes > combine_in_time_minute and not clock_in_flag:
        # print("Clock in time is greater than current time")
        # if employee is not clocked in current day
        if not punch_object:
            # print("Employee first clock in")
            if is_weekly_off != "#28a745":
                Punch.objects.create(
                    user=employee,
                    WfhOrWfo=location,
                    first_clock_in_time=current_time,
                    is_first_clocked_in=True,
                    punch_in_count=1,
                    is_shift_one=True,
                    last_punch_type=1,
                    status='AN' if is_anomaly else 'P',
                    in_time_anomaly=True,
                    ip_address=IP_address,
                    date=now.date()
                )
                clock_in_flag = True
                # print("Today is weekly off")

            elif checking_holiday:
                # print("Today is holiday")
                Punch.objects.create(
                    user=employee,
                    WfhOrWfo=location,
                    first_clock_in_time=current_time,
                    is_first_clocked_in=True,
                    punch_in_count=1,
                    is_shift_one=True,
                    last_punch_type=1,
                    status="AN",
                    is_holiday_work=True,
                    in_time_anomaly=True,
                    ip_address=IP_address,
                    date=now.date(),
                )
                clock_in_flag = True
            elif is_anomaly and not clock_in_flag:
                Punch.objects.create(
                    user=employee,
                    WfhOrWfo=location,
                    first_clock_in_time=current_time,
                    is_first_clocked_in=True,
                    punch_in_count=1,
                    is_shift_one=True,
                    last_punch_type=1,
                    status='AN',
                    in_time_anomaly=True,
                    ip_address=IP_address,
                    date=now.date()
                )
                clock_in_flag = True
                # print("Clock in anomaly")
            else:
                Punch.objects.create(
                    user=employee,
                    WfhOrWfo=location,
                    first_clock_in_time=current_time,
                    is_first_clocked_in=True,
                    punch_in_count=1,
                    is_shift_one=True,
                    last_punch_type=1,
                    status='P',
                    ip_address=IP_address,
                    date=now.date()
                )
                clock_in_flag = True
                # print("Clock in not anomaly")

            # print("________________________________________________________________")
        # employee clocked in current day
        else:
            # print("Second punch in")
            if current_time_minutes > combined_second_in_time_minutes:
                # print("Current time is greater than after break")
                if is_anomaly:
                    punch_object.is_second_clocked_in = True
                    punch_object.second_clock_in_time = current_time
                    punch_object.punch_in_count += 1
                    punch_object.is_shift_two = True
                    punch_object.in_time_anomaly = True
                    punch_object.status = "AN"
                    punch_object.last_punch_type = 1
                    punch_object.WfhOrWfo=location
                    punch_object.save()
                else:
                    punch_object.is_second_clocked_in = True
                    punch_object.second_clock_in_time = current_time
                    punch_object.punch_in_count += 1
                    punch_object.is_shift_two = True
                    punch_object.status = punch_object.status
                    punch_object.last_punch_type = 1
                    punch_object.WfhOrWfo=location
                    punch_object.save()
            else:
                punch_object.is_second_clocked_in = True
                punch_object.second_clock_in_time = current_time
                punch_object.punch_in_count += 1
                punch_object.last_punch_type = 1
                punch_object.is_shift_two = True
                punch_object.status = punch_object.status
                punch_object.WfhOrWfo=location
                punch_object.save()
            # print("****************************************************")
    elif not clock_in_flag:
        if is_weekly_off != "#28a745" and not clock_in_flag:
            Punch.objects.create(
                user=employee,
                WfhOrWfo=location,
                first_clock_in_time=current_time,
                is_first_clocked_in=True,
                punch_in_count=1,
                is_shift_one=True,
                last_punch_type=1,
                status='P',
                is_week_work=True,
                ip_address=IP_address,
                date=now.date()
            )
            clock_in_flag = True
            # print("Clock in time is good and today is week day")
        elif checking_holiday and not clock_in_flag:

            Punch.objects.create(
                user=employee,
                WfhOrWfo=location,
                first_clock_in_time=current_time,
                is_first_clocked_in=True,
                punch_in_count=1,
                is_shift_one=True,
                last_punch_type=1,
                status="P",
                is_holiday_work=True,
                in_time_anomaly=True,
                ip_address=IP_address,
                date=now.date(),
            )
            clock_in_flag = True
            # print("Clock in time is good and today is holiday")
        else:
            # print("Clock in time is good and status is present")
            Punch.objects.create(
                user=employee,
                WfhOrWfo=location,
                first_clock_in_time=current_time,
                is_first_clocked_in=True,
                punch_in_count=1,
                is_shift_one=True,
                last_punch_type=1,
                status='P',
                ip_address=IP_address,
                date=now.date()
            )
        print("=============================================================")
