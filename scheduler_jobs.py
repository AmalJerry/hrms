from datetime import time
from datetime import datetime, timedelta
from decimal import Decimal  # , date
# from decimal import Decimal
from app1.models import CompanyRules, User, Punch, HolidayList, HolidayLocationList, AssignWorkWeek, assignrule, CompOff
from django.db.models import Q
# from django.db import transaction
from django.utils import timezone
import arrow
from calendar import monthcalendar


""" Test Case """

""" Time Delta converter """


def timedelta_from_datetime_or_time(input_time):
    if isinstance(input_time, datetime):
        return datetime.now() - input_time
    elif isinstance(input_time, time):
        # Constructing timedelta directly from input time
        return timedelta(hours=input_time.hour, minutes=input_time.minute, seconds=input_time.second, microseconds=input_time.microsecond)
    else:
        print("Input must be either datetime.datetime or datetime.time")
        pass
        # below code is for test case
        # raise TypeError(
        #     "Input must be either datetime.datetime or datetime.time")


"""Get Leaves """


def get_half_day_leave(leave_data):
    if leave_data.Selecthalf1 == "first half" and leave_data.Selecthalf2 == "first half":
        return "first half"
    elif leave_data.Selecthalf1 == "second half" and leave_data.Selecthalf2 == "second half":
        return "second half"


def get_leave_data(employee, now):
    leave_data = employee.leave_set.filter(
        strtDate__lte=now.date(), endDate__gte=now.date(),
        Appliedon__lte=now.date(), status='Approved'
    ).order_by('-strtDate')

    leave_array = []
    
    if leave_data.exists():
        for leave_entry in leave_data:
            print("Leave data: ", leave_data)
            if len(leave_data) >= 1:
                print('leave entry: ', type(leave_entry.Days))
                if leave_entry.Days == 0.5:
                    leave_array.append(get_half_day_leave(leave_entry))
                elif leave_entry.Days == 1.0:
                    return 'full day'
                elif leave_entry.Days > 1:
                    print("Leave entry is greater than 1")
                    if leave_entry.Selecthalf1 == leave_entry.Selecthalf2:
                        print('One')
                        leave_array.append(get_half_day_leave(leave_entry))
                    if leave_entry.strtDate == now.date() and '.5' in str(leave_entry.Days):
                        print('One')
                        leave_array.append(get_half_day_leave(leave_entry))
                    if leave_entry.Selecthalf1 == "first half"  and leave_entry.Selecthalf2 == "second half":
                        return "full day"
                    if leave_entry.Selecthalf1 == "second half"  and leave_entry.Selecthalf2 == "first half":
                        return "full day" 
            else:
                if leave_entry.Days == 0.5:
                    return get_half_day_leave(leave_entry)
                elif leave_entry.Days == 1.0:
                    return 'full day'
                elif leave_entry.Days > 1:
                    if leave_entry.Selecthalf1 == leave_entry.Selecthalf2:
                        return get_half_day_leave(leave_entry)
                    if leave_entry.strtDate == now.date() and '.5' in str(leave_entry.Days):
                        return get_half_day_leave(leave_entry)
                    if leave_entry.Selecthalf1 == "first half" and leave_entry.Selecthalf2 == "second half":
                        return "full day"
                    if leave_entry.Selecthalf1 == "second half" and leave_entry.Selecthalf2 == "first half":
                        return "full day"

        print("Leave array: ", leave_array)
        if leave_array[0] != leave_array[1]:
            return 'full day'
        else:
            return leave_array[0]
    else:
        print(" ~~~~~~~~~~~~~~~~No Leave~~~~~~~~~~~~~~~~~")
        return None  # Handle case where no leave data is found


""" Get Durations """


def get_full_hour(full_hour, full_minutes):

    full_day = timedelta(minutes=full_hour * 60 + full_minutes)
    return full_day


def get_half_hour(half_hour, half_minutes):
    half_day = timedelta(minutes=half_hour * 60 + half_minutes)
    return half_day


def get_break_duration(org_in_time=None, org_out_time=None, attendance_rule=None):
    full_hour = get_full_hour(
        attendance_rule.fullhours, attendance_rule.fullminutes)
    # half_hour = get_half_hour(
    #     attendance_rule.rules_applied.halfhours, attendance_rule.rules_applied.halfminutes)
    org_work_duration = arrow.get(
        str(org_out_time), "HH:mm:ss") - arrow.get(str(org_in_time), "HH:mm:ss")

    difference_between_org_time_duraion_and_inTime_outTime_duraion = org_work_duration - full_hour

    if not difference_between_org_time_duraion_and_inTime_outTime_duraion < timedelta(hours=0, minutes=0, seconds=0):
        break_duration = difference_between_org_time_duraion_and_inTime_outTime_duraion
        return break_duration


def get_work_duration(punch_object, current_time, org_in_time=None, org_out_time=None, attendance_rule=None):
    if punch_object.is_first_clocked_in is True and punch_object.first_clock_in_time is not None:
        first_clocked_in_time = punch_object.first_clock_in_time
    else:
        first_clocked_in_time = time(hour=0, minute=0, second=0)

    if punch_object.is_first_clocked_out is True and punch_object.first_clock_out_time is not None:
        first_clocked_out_time = punch_object.first_clock_out_time
    else:
        first_clocked_out_time = time(hour=0, minute=0, second=0)

    first_clocked_in_time = datetime.strptime(
        str(first_clocked_in_time), "%H:%M:%S").time()
    first_clocked_out_time = datetime.strptime(
        str(first_clocked_out_time), "%H:%M:%S").time()

    break_duration = get_break_duration(
        org_in_time, org_out_time, attendance_rule)

    if punch_object.is_first_clocked_in and punch_object.is_first_clocked_out and not punch_object.is_second_clocked_in:

        work_duration = timedelta_from_datetime_or_time(
            first_clocked_out_time) - timedelta_from_datetime_or_time(first_clocked_in_time)
        return work_duration
    elif punch_object.is_first_clocked_in and not punch_object.is_first_clocked_out:

        work_duration = timedelta_from_datetime_or_time(
            current_time) - timedelta_from_datetime_or_time(first_clocked_in_time)
        return work_duration
    elif punch_object.is_first_clocked_in and punch_object.is_first_clocked_out and punch_object.is_second_clocked_in:
        work_duration = timedelta_from_datetime_or_time(
            current_time) - timedelta_from_datetime_or_time(first_clocked_in_time)
        if break_duration < work_duration:
            return work_duration - break_duration
        elif break_duration > work_duration:
            return break_duration - work_duration
        return work_duration


""" Off day funcionalites"""


def check_holiday_off(employee, now):
    holiday_list = HolidayList.objects.filter(
        Myuser_13__in=[employee.id, employee.admin_id],
        HolidayDate=now.strftime('%d %B %Y')
    )
    return holiday_list


def get_holiday(employee, holiday_list):
    for holiday in holiday_list:
        holiday_location = HolidayLocationList.objects.filter(
            Q(Holiday_List=holiday))
        for location in holiday_location:
            work_location = location.HolidayLocation.first().location
            is_optional = location.HolidayToggleBtn_ON
            if employee.wrklcn and employee.wrklcn.location == work_location and is_optional == 'off':
                return True
        return False


def check_workweek_off(employee, current_date):

    try:
        workweek_record = AssignWorkWeek.objects.get(user_id=employee)
        date_data = monthcalendar(current_date.year, current_date.month)

        day_fields = [f"day_{day}" for day in range(1, 36)]
        for day_index, day in enumerate([day for week in date_data for day in week]):
            day_field_index = day_index % 35
            day_field = day_fields[day_field_index]
            if day == current_date.day:
                day_value = getattr(
                    workweek_record.rules_applied, day_field)
                # print("============== Day value ==============", day_value)
                return day_value
        return "#28a745"
    except AssignWorkWeek.DoesNotExist:
        return "#28a745"


""" Get clock out """


def check_clock_out(employee, punch_data, rules_applied, is_auto_clock_out, is_anomaly, is_comp_off_enabled, previous_rules, comp_off_rule, employee_loss_of_pay_rules, now):
    try:
        current_time = now.time()
        print("Employee Loss of pay: ", employee_loss_of_pay_rules)
        leave_data = get_leave_data(employee, now)
        effective_date = now.date().strftime('%d %B %Y')
        # org_in_time = rules_applied.inTime
        # org_out_time = rules_applied.outTime
        full_day = get_full_hour(
            rules_applied.fullhours, rules_applied.fullminutes) if rules_applied is not None else ""
        half_day = get_half_hour(
            rules_applied.halfhours, rules_applied.halfminutes) if rules_applied is not None else ""

        org_in_time = getattr(
            rules_applied, "inTime", time(hour=0, minute=0, second=0))
        org_out_time = getattr(
            rules_applied, "outTime", time(hour=0, minute=0, second=0))
        today_holiday_list = check_holiday_off(employee, now)
        if punch_data.is_first_clocked_in == True and punch_data.is_first_clocked_out == True and not punch_data.is_second_clocked_in:
            first_clock_out_time_minutes = (
                punch_data.first_clock_out_time.hour, punch_data.first_clock_out_time.minute)
            org_clock_out_minutes = (org_out_time.hour, org_out_time.minute)

            if today_holiday_list:
                today_holiday = get_holiday(employee, today_holiday_list)
            else:
                today_holiday = None
            today_weekday = check_workweek_off(employee, now.date())
            print("Today is holiday: ", today_holiday)
            print("Today is weekday: ", today_weekday)
            if today_holiday:
                print("Holiday yes")
                work_duration = get_work_duration(
                    punch_data, now.time(), org_in_time, org_out_time, rules_applied)

                if work_duration <= half_day:
                    punch_data.status = "P"
                    punch_data.save()
                    if not previous_rules and is_comp_off_enabled:
                        print("comp off enabled and not created")
                        assign_rule = assignrule.objects.create(
                            user_id=employee,
                            effective_date=effective_date,
                            creditedleaves=0.5,
                            appliedleaves=0,
                            penaltydeduction=0,
                            leavebalance=0.5,
                        )
                        assign_rule.rules_applied.add(
                            comp_off_rule.id)
                    elif previous_rules and is_comp_off_enabled:
                        print("comp off enabled and already created")
                        previous_rules.creditedleaves = int(
                            previous_rules.creditedleaves) + 0.5
                        previous_rules.leavebalance = int(
                            previous_rules.leavebalance) + 0.5
                        previous_rules.save()
                        if not CompOff.objects.filter(punch_data=punch_data):
                            CompOff.objects.create(
                                user=employee, punch_data=punch_data, creditedleaves=0.5)
                else:
                    punch_data.status = "P"
                    punch_data.save()
                    if not previous_rules and is_comp_off_enabled:
                        assign_rule = assignrule.objects.create(
                            user_id=employee,
                            effective_date=effective_date,
                            creditedleaves=1,
                            appliedleaves=0,
                            penaltydeduction=0,
                            leavebalance=1,
                        )
                        assign_rule.rules_applied.add(
                            comp_off_rule.id)
                        print("comp off enabled and not created")
                    elif previous_rules and is_comp_off_enabled:
                        previous_rules.creditedleaves = int(
                            previous_rules.creditedleaves) + 1
                        previous_rules.leavebalance = int(
                            previous_rules.leavebalance) + 1
                        previous_rules.save()
                        if not CompOff.objects.filter(punch_data=punch_data).exists():
                            CompOff.objects.create(
                                user=employee, punch_data=punch_data, creditedleaves=1)
                        print("comp off enabled and already created")
            elif today_weekday != "#28a745":
                print("work week yes")
                work_duration = get_work_duration(
                    punch_data, now.time(), org_in_time, org_out_time, rules_applied)
                if work_duration <= half_day:
                    punch_data.status = "P"
                    punch_data.save()
                    if not previous_rules and is_comp_off_enabled:
                        assign_rule = assignrule.objects.create(
                            user_id=employee,
                            effective_date=effective_date,
                            creditedleaves=0.5,
                            appliedleaves=0,
                            penaltydeduction=0,
                            leavebalance=0.5,
                        )
                        assign_rule.rules_applied.add(
                            comp_off_rule.id)
                        print("comp off enabled and not created")
                    elif previous_rules and is_comp_off_enabled:
                        previous_rules.creditedleaves = int(
                            previous_rules.creditedleaves) + 0.5
                        previous_rules.leavebalance = int(
                            previous_rules.leavebalance) + 0.5
                        previous_rules.save()
                        if not CompOff.objects.filter(punch_data=punch_data).exists():
                            CompOff.objects.create(
                                user=employee, punch_data=punch_data, creditedleaves=0.5)
                else:
                    punch_data.status = "P"
                    punch_data.save()
                    if not previous_rules and is_comp_off_enabled:
                        assign_rule = assignrule.objects.create(
                            user_id=employee,
                            effective_date=effective_date,
                            creditedleaves=1,
                            appliedleaves=0,
                            penaltydeduction=0,
                            leavebalance=1,
                        )
                        assign_rule.rules_applied.add(
                            comp_off_rule.id)
                        print("comp off enabled and not created")
                    elif previous_rules and is_comp_off_enabled:
                        previous_rules.creditedleaves = int(
                            previous_rules.creditedleaves) + 1
                        previous_rules.leavebalance = int(
                            previous_rules.leavebalance) + 1
                        previous_rules.save()
                        if not CompOff.objects.filter(punch_data=punch_data).exists():
                            CompOff.objects.create(
                                user=employee, punch_data=punch_data, creditedleaves=1)

            elif first_clock_out_time_minutes < org_clock_out_minutes and leave_data is None:
                punch_data.status = "AN"
                punch_data.out_time_anomaly = True
                punch_data.save()
                employee_loss_of_pay_rules.penaltydeduction += Decimal(0.5)
                employee_loss_of_pay_rules.save()

        # Checking the employee first clocked in and not first clocked out
        elif punch_data.is_first_clocked_in == True and not punch_data.is_first_clocked_out:
            work_duration = get_work_duration(
                punch_data, current_time, org_in_time, org_out_time, rules_applied)
            print("Work Duration: ", work_duration)
            if is_auto_clock_out:
                punch_data.first_clock_out_time = rules_applied.outTime
                punch_data.is_first_clocked_out = True
                punch_data.punch_out_count += 1
                punch_data.last_punch_type = 2
                punch_data.status = "AC"
                punch_data.work_duration = str(work_duration)
                punch_data.save()
                return True
            else:
                punch_data.first_clock_out_time = time(
                    hour=21, minute=0, second=0)
                punch_data.is_first_clocked_out = True
                punch_data.last_punch_type = 2
                punch_data.status = 'AN' if is_anomaly else punch_data.status
                punch_data.work_duration = str(work_duration)
                punch_data.out_time_anomaly = True
                punch_data.punch_out_count += 1
                punch_data.save()
                # if punch_data.status == "AN" and punch_data.in_time_anomaly or work_duration < full_day:
                #     employee_loss_of_pay_rules.penaltydeduction += Decimal(0.5)
                #     employee_loss_of_pay_rules.save()
                return True

        # Checking the employee first clocked in, first clocked out, second clocked in and not second clocked out
        elif punch_data.is_first_clocked_in and punch_data.is_first_clocked_out and punch_data.is_second_clocked_in and not punch_data.is_second_clocked_out:
            work_duration = get_work_duration(
                punch_data, current_time, org_in_time, org_out_time, rules_applied)

            if is_auto_clock_out:
                punch_data.second_clock_out_time = rules_applied.outTime
                punch_data.is_second_clocked_out = True
                punch_data.punch_out_count += 1
                punch_data.last_punch_type = 2
                punch_data.status = "AC"
                punch_data.work_duration = str(work_duration)
                punch_data.save()
                return True
            else:
                punch_data.second_clock_out_time = time(
                    hour=21, minute=0, second=0)
                punch_data.is_second_clocked_out = True
                punch_data.last_punch_type = 2
                punch_data.status = 'AN' if is_anomaly else punch_data.status
                punch_data.work_duration = str(work_duration)
                punch_data.out_time_anomaly = True
                punch_data.punch_out_count += 1
                punch_data.save()
                # if punch_data.status == "AN" and punch_data.in_time_anomaly or work_duration < full_day:
                #     employee_loss_of_pay_rules += Decimal(0.5)
                #     employee_loss_of_pay_rules.save()
                return True
        elif leave_data == "first half":
            work_duration = get_work_duration(
                punch_data, current_time, org_in_time, org_out_time, rules_applied)
            print("First half leave data: ", work_duration)
            half_work_duration = get_half_hour(
                rules_applied.halfhours, rules_applied.halfminutes)
            if work_duration < half_work_duration:
                punch_data.status = "AN"
                punch_data.work_duration_anomaly = True
                punch_data.save()
                if employee_loss_of_pay_rules:
                    employee_loss_of_pay_rules.penaltydeduction += Decimal(0.5)
                    employee_loss_of_pay_rules.save()
            return True
        elif leave_data == "second half":
            work_duration = get_work_duration(
                punch_data, current_time, org_in_time, org_out_time, rules_applied)
            print("Second half leave data: ", work_duration)
            half_work_duration = get_half_hour(
                rules_applied.halfhours, rules_applied.halfminutes)
            if work_duration < half_work_duration:
                punch_data.status = "AN"
                punch_data.work_duration_anomaly = True
                punch_data.save()
                if employee_loss_of_pay_rules:
                    employee_loss_of_pay_rules.penaltydeduction += Decimal(0.5)
                    employee_loss_of_pay_rules.save()
            return True
        else:
            print("Someting is okey")
            pass
    except Exception as e:
        print("Exception: ", e)
        # raise e
        pass
# get employee punch data


def get_punch_data(employee, current_date):
    try:
        punch_data = Punch.objects.get(user=employee, date__date=current_date)
        return punch_data
    except Punch.DoesNotExist:
        return False


def update_attendance():

    now = timezone.now()
    print("Timmezone: ", now, now.time())
    employees = User.objects.filter(status='Active').prefetch_related(
        'punch_set', 'leave_set', 'assignattendancerule_set',
    )
    try:
        for employee in employees:
            comp_off_rule = CompanyRules.objects.filter(
                admin_id__in=[employee.id, employee.admin_id], leavename='Comp Off').first()
            company_penalty_rule = CompanyRules.objects.filter(
                admin_id__in=[employee.id, employee.admin_id], leavename='Loss Of Pay').first()

            print('Employee ====> ', employee,
                  now.time().replace(microsecond=0))

            attendance_rule = employee.assignattendancerule_set.first()
            rules_applied = attendance_rule.rules_applied if attendance_rule else None

            is_comp_off_enabled = getattr(rules_applied, "enable_CO", False)
            previous_rules = assignrule.objects.filter(
                user_id=employee, rules_applied__id=comp_off_rule.id if comp_off_rule else 0).first()
            employee_loss_of_pay_rules = assignrule.objects.filter(
                user_id=employee, rules_applied__id=company_penalty_rule.id if company_penalty_rule else 0).first()

            is_auto_clock_out = rules_applied.auto_CO if rules_applied else False
            is_anomaly = rules_applied.enable_AT if rules_applied else False

            punch_data = get_punch_data(employee, now.date())

            work_week = check_workweek_off(employee, now.date())
            get_holiday_list = check_holiday_off(employee, now)
            if get_holiday_list:
                checking_holiday_off = get_holiday(employee, get_holiday_list)
            else:
                checking_holiday_off = None
            try:
                if punch_data:
                    check_clock_out(employee, punch_data, rules_applied,
                                    is_auto_clock_out, is_anomaly, is_comp_off_enabled, previous_rules, comp_off_rule, employee_loss_of_pay_rules,  now)
                else:

                    leave_data = get_leave_data(employee, now)
                    # print("Leave Data: ", leave_data)
                    if leave_data == "full day":
                        print("Full day leave")
                        Punch.objects.get_or_create(
                            user=employee, date=now.date(), status='L', is_first_clocked_in=True, is_first_clocked_out=True, last_punch_type=2)
                    elif leave_data == "first half":
                        Punch.objects.get_or_create(
                            user=employee, date=now.date(), status='A', is_first_clocked_in=True, is_first_clocked_out=True, last_punch_type=2)
                        print("First half leave")
                    elif leave_data == "second half":
                        Punch.objects.get_or_create(
                            user=employee, date=now.date(), status='A', is_first_clocked_in=True, is_first_clocked_out=True, last_punch_type=2)
                        print("Second half leave")
                    elif work_week != "#28a745":
                        print("Weekly Off")
                        Punch.objects.get_or_create(
                            user=employee, date=now.date(), status='WO', is_first_clocked_in=True, is_first_clocked_out=True, last_punch_type=2)
                        print("Today is week day")
                    elif checking_holiday_off:
                        print("Today is holiday")
                        Punch.objects.get_or_create(
                            user=employee, date=now.date(), status='H', is_first_clocked_in=True, is_first_clocked_out=True, last_punch_type=2)
                    else:
                        print("Absent!")
                        Punch.objects.get_or_create(
                            user=employee,
                            date=now.date(),
                            status='A',
                            is_first_clocked_in=True,
                            is_first_clocked_out=True,
                            last_punch_type=2
                        )
                        if employee_loss_of_pay_rules:
                            employee_loss_of_pay_rules.penaltydeduction += Decimal(
                                1)
                            employee_loss_of_pay_rules.save()
            except Exception as e:
                print("Exception: ", e)
                # raise Exception(e)
                pass
            print("======================================================")
            print("\n\n")
    except Exception as e:
        print("Exception: ", e)
        # raise Exception(e)
        pass

def delete_duplicate_attendance():
    try:
        print('delete_duplicate_attendance')
        now = timezone.now()
        print(now.date())
        employees = User.objects.filter(status='Active').prefetch_related(
        'punch_set', 'leave_set', 'assignattendancerule_set',)
        
        duplicate_punch_query = []
        to_delete_id = []

        for employee in employees:
            punches_in_today = Punch.objects.filter(date=now.date(), user__id=employee.id)
            if punches_in_today.count() > 1:
                    punches_in_today.last().delete()
                    print(f'punch deleted for {employee.email}')
        return 'Success'
    except Exception as e:
        print("Exception: ", e)
        # raise Exception(e)
        pass

""" End"""
