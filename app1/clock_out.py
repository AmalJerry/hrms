from decimal import Decimal
from django.utils import timezone
from .models import CompanyRules, Punch, Leave, assignrule
import arrow
from datetime import datetime, time, timedelta

"""
Time Delta Converter
"""


def timedelta_from_datetime_or_time(input_time):
    if isinstance(input_time, datetime):
        return datetime.now() - input_time
    elif isinstance(input_time, time):
        # Constructing timedelta directly from input time
        return timedelta(hours=input_time.hour, minutes=input_time.minute, seconds=input_time.second, microseconds=input_time.microsecond)
    else:
        raise TypeError(
            "Input must be either datetime.datetime or datetime.time")


""" Get Off day Data"""


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
    elif leave_data and leave_data.Days > 1:
        if leave_data.Selecthalf1 == leave_data.Selecthalf2:
            return get_half_day_leave(leave_data)
        if leave_data.strtDate == now.date() and '.5' in str(leave_data.Days):

            return get_half_day_leave(leave_data)


"""
    Time Duration finding functions 
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

    if not difference_between_org_time_duraion_and_inTime_outTime_duraion < timedelta(hours=0, minutes=0, seconds=0):
        break_start_time = datetime.combine(
            datetime.today(), org_in_time) + half_hour
        return break_start_time.time()
    else:
        return time(hour=0, minute=0, second=0)


def get_break_end_time(org_in_time, org_out_time, attendance_rule):

    full_hour = get_full_hour(
        attendance_rule.rules_applied.fullhours, attendance_rule.rules_applied.fullminutes)
    # half_hour = get_half_hour(
    #     attendance_rule.rules_applied.halfhours, attendance_rule.rules_applied.halfminutes)
    org_work_duration = arrow.get(
        str(org_out_time), "HH:mm:ss") - arrow.get(str(org_in_time), "HH:mm:ss")

    difference_between_org_time_duraion_and_inTime_outTime_duraion = org_work_duration - full_hour
    if not difference_between_org_time_duraion_and_inTime_outTime_duraion < timedelta(hours=0, minutes=0, seconds=0):
        break_end_time = datetime.combine(
            datetime.today(), org_in_time) + difference_between_org_time_duraion_and_inTime_outTime_duraion
        return break_end_time.time()


def get_break_duration(org_in_time, org_out_time, attendance_rule):
    full_hour = get_full_hour(
        attendance_rule.rules_applied.fullhours, attendance_rule.rules_applied.fullminutes)
    # half_hour = get_half_hour(
    #     attendance_rule.rules_applied.halfhours, attendance_rule.rules_applied.halfminutes)
    org_work_duration = arrow.get(
        str(org_out_time), "HH:mm:ss") - arrow.get(str(org_in_time), "HH:mm:ss")

    difference_between_org_time_duraion_and_inTime_outTime_duraion = org_work_duration - full_hour

    if not difference_between_org_time_duraion_and_inTime_outTime_duraion < timedelta(hours=0, minutes=0, seconds=0):
        break_duration = difference_between_org_time_duraion_and_inTime_outTime_duraion
        return break_duration


def get_work_duration(punch_object, current_time, org_in_time=None, org_out_time=None, attendance_rule=None):
    if punch_object.is_first_clocked_in and not punch_object.is_first_clocked_out:
        work_duration = timedelta_from_datetime_or_time(
            current_time) - timedelta_from_datetime_or_time(punch_object.first_clock_in_time)
        return work_duration
    if punch_object.is_first_clocked_in and punch_object.is_first_clocked_out and punch_object.is_second_clocked_in and not punch_object.is_second_clocked_out:
        break_duration = get_break_duration(
            org_in_time, org_out_time, attendance_rule)
        work_duration = timedelta_from_datetime_or_time(
            current_time) - timedelta_from_datetime_or_time(punch_object.first_clock_in_time)

        if break_duration < work_duration:
            return work_duration - break_duration
        elif break_duration > work_duration:
            return break_duration - work_duration
        # return work_duration


def clocked_out(employee, punch_object, attendance_rule):

    now = timezone.now()
    time_format = "%H:%M:%S"
    # Normal time Variable
    current_time = now.time().replace(microsecond=0)
    org_in_time = getattr(attendance_rule.rules_applied, "inTime")
    org_out_time = getattr(attendance_rule.rules_applied, "outTime")
    end_time_limit = datetime.strptime(
        str(org_out_time), time_format) + timedelta(hours=5)

    print("Current Time =======> :", current_time)
    out_grace_period = getattr(attendance_rule.rules_applied, "outGracePeriod", now.time(
    )) if attendance_rule else now.time()
    full_work_duration = get_full_hour(
        attendance_rule.rules_applied.fullhours, attendance_rule.rules_applied.fullminutes)  # regular work duration

    total_work_durations = get_work_duration(
        punch_object, current_time, org_in_time, org_out_time, attendance_rule)  # employee work duration

    # tupled times for condition
    current_time_minutes = (current_time.hour, current_time.minute)
    org_out_time_minutes = (org_out_time.hour, org_out_time.minute)
    combine_out_time = combined_in_time(org_out_time, out_grace_period)
    combine_out_time_minute = (combine_out_time.hour, combine_out_time.minute)
    end_time_limit_minute = (end_time_limit.hour, end_time_limit.minute)

    is_anomaly = getattr(attendance_rule.rules_applied, "enable_AT", False)
    half_leave_data = get_leave_data(employee, now)
    # if the user Apply any leave(Second Half)
    break_start_time = get_break_start_time(
        org_in_time, org_out_time, attendance_rule)
    break_start_time_minutes = (break_start_time.hour, break_start_time.minute)

    half_day = get_half_hour(
        attendance_rule.rules_applied.halfhours, attendance_rule.rules_applied.halfminutes)
    company_penalty_rule = CompanyRules.objects.filter(
        admin_id__in=[employee.id, employee.admin_id], leavename='Loss Of Pay').first()
    employee_loss_of_pay_rules = assignrule.objects.filter(
        user_id=employee, rules_applied__id=company_penalty_rule.id if company_penalty_rule else 0).first()

    # Checking half day leave
    if half_leave_data == "second half":

        if current_time_minutes < break_start_time_minutes and total_work_durations < half_day:
            punch_object.is_first_clocked_out = True
            punch_object.first_clock_out_time = current_time
            punch_object.punch_out_count += 1
            punch_object.out_time_anomaly = True
            punch_object.work_duration_anomaly = True
            punch_object.status = "AN"
            punch_object.last_punch_type = 2
            punch_object.save()
        else:
            punch_object.is_first_clocked_out = True
            punch_object.first_clock_out_time = current_time
            punch_object.punch_out_count += 1
            punch_object.status = "HL"
            punch_object.last_punch_type = 2
            punch_object.save()
    # checking current time greater than End time limit
    elif current_time_minutes > end_time_limit_minute:
        if is_anomaly and total_work_durations < full_work_duration:
            # print("Hell Yeah!")
            if not punch_object.is_first_clocked_out:
                punch_object.is_first_clocked_out = True
                punch_object.first_clock_out_time = current_time
                punch_object.punch_out_count += 1
                punch_object.out_time_anomaly = True
                punch_object.status = "AN"
                punch_object.last_punch_type = 2
                punch_object.save()
                if employee_loss_of_pay_rules:
                    employee_loss_of_pay_rules.penaltydeduction += Decimal(1.0)
                    employee_loss_of_pay_rules.save()
            elif punch_object.is_first_clocked_out and not punch_object.is_second_clocked_out:
                punch_object.is_second_clocked_out = True
                punch_object.second_clock_out_time = current_time
                punch_object.punch_out_count += 1
                punch_object.out_time_anomaly = True
                punch_object.status = "AN"
                punch_object.last_punch_type = 2
                punch_object.save()
                if employee_loss_of_pay_rules:
                    employee_loss_of_pay_rules.penaltydeduction += Decimal(1.0)
                    employee_loss_of_pay_rules.save()
        else:
            if not punch_object.is_first_clocked_out:
                punch_object.is_first_clocked_out = True
                punch_object.first_clock_out_time = current_time
                punch_object.punch_out_count += 1
                punch_object.status = punch_object.status
                punch_object.last_punch_type = 2
                punch_object.save()
            elif punch_object.is_first_clocked_out and not punch_object.is_second_clocked_out:
                punch_object.is_second_clocked_out = True
                punch_object.second_clock_out_time = current_time
                punch_object.punch_out_count += 1
                punch_object.status = punch_object.status
                punch_object.last_punch_type = 2
                punch_object.save()
    elif current_time_minutes < org_out_time_minutes and punch_object.is_first_clocked_in and punch_object.is_first_clocked_out:
        print("Not as much as good~", total_work_durations, full_work_duration)
        if not punch_object.is_first_clocked_out:
            print("First clock out")
            punch_object.is_first_clocked_out = True
            punch_object.first_clock_out_time = current_time
            punch_object.punch_out_count += 1
            punch_object.out_time_anomaly = True
            punch_object.work_duration_anomaly = True
            punch_object.status = "AN"
            punch_object.last_punch_type = 2
            punch_object.save()
        elif punch_object.is_first_clocked_out and not punch_object.is_second_clocked_out:
            print("Second clock out")
            punch_object.is_second_clocked_out = True
            punch_object.second_clock_out_time = current_time
            punch_object.punch_out_count += 1
            punch_object.out_time_anomaly = True
            punch_object.work_duration_anomaly = True
            punch_object.status = "AN"
            punch_object.last_punch_type = 2
            punch_object.save()
    else:
        if not punch_object.is_first_clocked_out:
            print('Help!')
            punch_object.is_first_clocked_out = True
            punch_object.first_clock_out_time = current_time
            punch_object.punch_out_count += 1
            punch_object.status = "HL" if punch_object.status == "HL" else punch_object.status
            punch_object.last_punch_type = 2
            punch_object.save()
        elif punch_object.is_first_clocked_out and not punch_object.is_second_clocked_out:
            print("Help!!")
            punch_object.is_second_clocked_out = True
            punch_object.second_clock_out_time = current_time
            punch_object.punch_out_count += 1
            punch_object.status = "HL" if punch_object.status == "HL" else punch_object.status
            punch_object.last_punch_type = 2
            punch_object.save()


"""
TODO:Check the early clock out time issue
TODO: Penalty is decreasing after admin apporves the Get Approval request
"""
