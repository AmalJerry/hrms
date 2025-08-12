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

def leavecredited():
    employee = User.objects.filter(status="Active")
    print("employee :", employee)
    for employee_id in employee:
        print("employee_id :", employee_id)

        assigned_rules = assignrule.objects.filter(user_id=employee_id)
        print("assigned_rules :", assigned_rules)
        today = date.today()

        for assign_rule in assigned_rules: 

            effective_date = datetime.strptime(assign_rule.effective_date, "%d %B %Y").date()

            leave_name = assign_rule.rules_applied.all().first().leavename
            print("leave_name :", leave_name)
            total_days = assign_rule.rules_applied.all().first().days
            carryforward = assign_rule.rules_applied.all().first().CarryForwardeEnabled
            accrualfrequency = assign_rule.rules_applied.all().first().AccrualFrequency
            accrualperiod = assign_rule.rules_applied.all().first().AccrualPeriod
            print("accrualfrequency ; AccrualPeriod :", accrualfrequency , accrualperiod)

            if leave_name not in ["Maternity Leave", "Optional Holiday"]:
                
                monthly_metrics = {
                    "column_name": ["Details"] + [calendar.month_abbr[i] for i in range(1, 13)],
                    "data": [
                        ["Credited Leaves"] + ["0.00"] * 12,
                        ["Applied Leaves"] + ["0.00"] * 12,
                        ["Penalty Deduction"] + ["-"] * 12,
                        ["Closing Balance"] + ["-"] * 12,
                    ],
                }

                getcontext().prec = 4

            else:

                monthly_metrics = {
                    "column_name": ["Details"] + [calendar.month_abbr[i] for i in range(1, 13)],
                    "data": [
                        ["Applied Leaves"] + ["0.00"] * 12,
                        ["Penalty Deduction"] + ["-"] * 12,
                        ["Closing Balance"] + ["-"] * 12,
                    ],
                }

                getcontext().prec = 3

            first_day_of_current_month = today.replace(day=1)
            previous_day = first_day_of_current_month - timedelta(days=1)
            print("Previous day: ", previous_day)

            previous_month_first_day = previous_day.replace(day=1)
            print("Previous month first day: ", previous_month_first_day)
            print("leave_name  :", leave_name)

            total_credited_leave = 0
            total_leave_balance = 0

            if carryforward == "on" and leave_name not in ["Maternity Leave", "Optional Holiday"]:
                current_month = effective_date
                print("current_month 1 :", current_month)
                while current_month <= previous_month_first_day:
                    if total_days > 0:
                        last_day_of_month = current_month.replace(day=calendar.monthrange(current_month.year, current_month.month)[1])
                        total_days_in_month = calendar.monthrange(current_month.year, current_month.month)[1]
                        print("last_day_of_month ; total_days_in_month :", last_day_of_month, total_days_in_month)

                        if current_month == effective_date:
                            total_day_in_month = (last_day_of_month - effective_date).days + 1
                            print("total_day_in_month :", total_day_in_month)
                        else:
                            total_day_in_month = total_days_in_month
                            print("total_day_in_month 2:", total_day_in_month)

                        one_month_credited_leave = total_days / 12
                        one_day_credited_leave = one_month_credited_leave / total_days_in_month
                        total_credited_leave_in_effective_date = one_day_credited_leave * total_day_in_month

                        total_credited_leave += total_credited_leave_in_effective_date
                        total_leave_balance += total_credited_leave_in_effective_date

                    current_month = current_month.replace(day=1) + relativedelta(months=1)

            print("total_credited_leave ; total_leave_balance :", total_credited_leave, total_leave_balance)  
            
            if effective_date.year != today.year:
                effective_date = datetime(today.year, 1, 1).date()
            else:
                effective_date = effective_date

            print("Effective_Date :", effective_date)

            previous_leave_balance = Decimal('0.00')
            previous_credited_leave = 0
            previous_credited_leave += Decimal(total_credited_leave)
            previous_applied_leave = 0
            previous_penalty_count = 0 
            rule_days = 1
            print("previous_credited_leave : ", previous_credited_leave)
            current_month = effective_date
            print("current_month 2920 : ", current_month)

            while current_month <= today:
                
                last_day_of_month = current_month.replace(day=calendar.monthrange(current_month.year, current_month.month)[1])

                total_days_in_month = calendar.monthrange(
                    current_month.year, current_month.month)[1]

                print("last_day_of_month , total_days_in_month : ",
                    last_day_of_month, total_days_in_month)

                # Calculate the total credited_leave for the current month
                if current_month == effective_date:
                    total_day_in_month = (last_day_of_month - effective_date).days + 1
                    print("total_day_in_month 1 : ",
                        effective_date, total_day_in_month)
                else:
                    total_day_in_month = calendar.monthrange(
                        current_month.year, current_month.month)[1]
                    print("total_day_in_month 2 : ", total_day_in_month)

                company_rule = assign_rule.rules_applied.all()

                # Checking which rule is need to show in HTML
                for cRule in company_rule:
                    # print('Inside the if condition: ')
                    print("CFE :", cRule.CarryForwardeEnabled)
                    if cRule.days > 0 and cRule.leavename not in ["Maternity Leave", "Optional Holiday"]:
                        print('in if : ', cRule.leavename)
                        onemonth_credited_leave = Decimal(cRule.days / 12)
                        print("onemonth_credited_leave : ",
                            onemonth_credited_leave)
                        one_day_credited_leave = onemonth_credited_leave / Decimal(total_days_in_month)
                        print("total_day_in_month , one_month_credited_leave , one_day_credited_leave :", total_day_in_month ,onemonth_credited_leave, one_day_credited_leave)

                        total_credited_leave = one_day_credited_leave * total_day_in_month
                        print("total_credited_leave 3 : ",total_credited_leave)

                        canceled_request = 0
                        rejected_request = 0
                        # Query the Leave table for the employee's leaves within the current month
                        leave_data = Leave.objects.filter(
                            applicant_email_id=employee_id,
                            strtDate__lte=last_day_of_month,
                            endDate__gte=current_month
                        ).values('leavetyp', 'Days', 'strtDate', 'endDate').annotate(
                            applied_leave=Sum('Days'),
                            canceled_request=Sum(
                                Case(When(cancel_requested=True, then='Days'),
                                    default=0, output_field=IntegerField())
                            ),
                            rejected_request=Sum(
                                Case(When(rejected=True, then='Days'),
                                    default=0, output_field=IntegerField())
                            ),
                        )

                        applied_leave_dict = {leave_type: Decimal(
                            '0.00') for leave_type in assign_rule.rules_applied.all()}
                        print("applied_leave_dict :", applied_leave_dict)
                        total_applied_leave = Decimal('0.00')
                        days = Decimal('0.00')
                        print("DAYS :", days)
                        for data in leave_data:
                            applied_leavename = data['leavetyp']
                            print("NAME :", applied_leavename, cRule.leavename)

                            print("DATA : ", data)

                            if applied_leavename == cRule.leavename:
                                leave_type = data['leavetyp']
                                applied_leave = Decimal(
                                    data['applied_leave'] or '0.00')
                                applied_leave_dict[leave_type] = applied_leave
                                print("leave_type :", leave_type, "applied_leave :", applied_leave,
                                    "applied_leave_dict[leave_type] : ", applied_leave_dict[leave_type])

                                canceled_request += data['canceled_request']
                                rejected_request += data['rejected_request']
                                total_applied_leave += applied_leave
                                print("total_applied_leave :", total_applied_leave)

                                if rejected_request >= 1:
                                    days += Decimal(data['Days'])
                                    print("days: ", days)

                        for leave_type in assign_rule.rules_applied.all().values_list('leavename', flat=True):

                            credited_leave = total_credited_leave
                            print("credited_leave 3000 : ", credited_leave)
                            applied_leave = applied_leave_dict.get(
                                leave_type, Decimal('0.00'))
                            print("applied_leave : ", applied_leave)
                            previous_applied_leave += total_applied_leave
                            print("prev_appL : ", previous_applied_leave)

                            if applied_leave == Decimal('0.00'):
                                print("previous_credited_leave 3005 : ",
                                    previous_credited_leave)
                                credited_leave += previous_credited_leave
                                print("credited_leave 3006 : ", credited_leave)
                            else:
                                if rejected_request >= 1:
                                    credited_leave += previous_credited_leave
                                    total_applied_leave -= days
                                    previous_applied_leave -= days
                                    print("credited_leave 3011 : ", credited_leave,
                                        total_applied_leave, previous_applied_leave)
                                    # previous_applied_leave -= applied_leave
                                    # applied_leave -= applied_leave_dict[leave_type]
                                    # print("preapp :", previous_applied_leave, applied_leave)

                                else:
                                    #     previous_credited_leave -= applied_leave
                                    print("applied_leave :", applied_leave)
                                    print("previous_credited_leave 3017: ",
                                        previous_credited_leave)
                                    credited_leave += previous_credited_leave
                                    print("credited_leave 3016 : ", credited_leave)

                            print("credited_leave ; crd : ",
                                credited_leave, total_credited_leave)
                            leave_balance = (
                                Decimal(credited_leave) - Decimal(previous_applied_leave))
                            print("leave_balance 3020 : ", leave_balance)

                            if applied_leave == Decimal('0.00'):
                                previous_credited_leave = credited_leave
                                print("previous_credited_leave 3023 : ",
                                    previous_credited_leave)
                            else:
                                previous_credited_leave = credited_leave
                                print("previous_credited_leave 3024 : ",
                                    previous_credited_leave)

                            print('leave_balance , credited_leave 3027: ',
                                leave_balance, credited_leave)
                            # Find the index for the current month and update the data
                            month_index = current_month.month
                            print("month_index 1 :", month_index)
                            # monthly_metrics["data"][0][month_index] = f"{total_credited_leave:.2f}"
                            if accrualfrequency == "Monthly" and accrualperiod == "Start":
                                monthly_metrics["data"][0][month_index] = f"{total_credited_leave:.2f}"
                                monthly_metrics["data"][1][month_index] = f"{total_applied_leave:.2f}"
                                monthly_metrics["data"][2][month_index] = "-"
                                monthly_metrics["data"][3][month_index] = f"{leave_balance:.2f}"

                                # previous_leave_balance = leave_balance
                                # print("previous_leave_balance : ",previous_leave_balance)
                                # assign_rule.creditedleaves = total_credited_leave
                                assign_rule.creditedleaves = credited_leave
                                assign_rule.appliedleaves = previous_applied_leave
                                assign_rule.leavebalance = leave_balance
                                assign_rule.save()
                                rule_days = 1

                                print("current_month bbbbbbbbbbbbbbbb :", current_month)
                                first_day_next_month = current_month.replace(day=1).replace(month=datetime.now().month + 1)
                                # Get the last day of the current month
                                last_day_current_month = first_day_next_month - timedelta(days=1)
                                print("first_day_next_month ; last_day_current_month :", first_day_next_month , last_day_current_month )

                            elif accrualfrequency == "Monthly" and accrualperiod == "End":
                                print("last_day_of_month : ", last_day_of_month)
                                if today >= last_day_of_month :
                                    monthly_metrics["data"][0][month_index] = f"{total_credited_leave:.2f}"
                                    monthly_metrics["data"][1][month_index] = f"{total_applied_leave:.2f}"
                                    monthly_metrics["data"][2][month_index] = "-"
                                    monthly_metrics["data"][3][month_index] = f"{leave_balance:.2f}"

                                    # previous_leave_balance = leave_balance
                                    # print("previous_leave_balance : ",previous_leave_balance)
                                    # assign_rule.creditedleaves = total_credited_leave
                                    assign_rule.creditedleaves = credited_leave
                                    assign_rule.appliedleaves = previous_applied_leave
                                    assign_rule.leavebalance = leave_balance
                                    assign_rule.save()
                                    rule_days = 1
                    
                    elif cRule.days > 0 and (cRule.leavename == "Maternity Leave" or cRule.leavename == "Optional Holiday"):
                        total_credited_leave = Decimal(total_days)
                        print("totalcredited_leave : ", total_credited_leave)
                        
                        canceled_request = 0
                        rejected_request = 0
                        leave_data = Leave.objects.filter(
                            applicant_email_id=employee_id,
                            strtDate__lte=last_day_of_month,
                            endDate__gte=current_month
                        ).values('leavetyp', 'Days', 'strtDate', 'endDate').annotate(
                            applied_leave=Sum('Days'),
                            canceled_request=Sum(
                                Case(When(cancel_requested=True, then='Days'),
                                    default=0, output_field=IntegerField())
                            ),
                            rejected_request=Sum(
                                Case(When(rejected=True, then='Days'),
                                    default=0, output_field=IntegerField())
                            ),
                        )

                        applied_leave_dict = {leave_type: Decimal('0.00') for leave_type in assign_rule.rules_applied.all()}
                        print("applied_leave_dict :", applied_leave_dict)
                        total_applied_leave = Decimal('0.00')
                        days = Decimal('0.00')
                        print("DAYS :", days)
                        for data in leave_data:
                            applied_leavename = data['leavetyp']
                            print("NAME :", applied_leavename, cRule.leavename)
                            print("DATA : ", data)
                            if applied_leavename == cRule.leavename:
                                leave_type = data['leavetyp']
                                applied_leave = Decimal(data['applied_leave'] or '0.00')
                                applied_leave_dict[leave_type] = applied_leave
                                print("leave_type :", leave_type, "applied_leave :", applied_leave, "applied_leave_dict[leave_type] : ", applied_leave_dict[leave_type])

                                canceled_request += data['canceled_request']
                                rejected_request += data['rejected_request']
                                total_applied_leave += applied_leave
                                print("total_applied_leave :", total_applied_leave)

                                if rejected_request >= 1:
                                    days += Decimal(data['Days'])
                                    print("days: ", days)
                        for leave_type in assign_rule.rules_applied.all().values_list('leavename', flat=True):
                            print("leave_type", leave_type)
                            credited_leave = total_credited_leave
                            print("credited_leave 4431 : ", credited_leave)
                            applied_leave = applied_leave_dict.get(leave_type, Decimal('0.00'))
                            print("applied_leave : ", applied_leave)
                            previous_applied_leave += total_applied_leave
                            print("prev_appL : ", previous_applied_leave)
                            if rejected_request >= 1:
                                total_applied_leave -= days
                                previous_applied_leave -= days
                                print("credited_leave 4439 : ", credited_leave, total_applied_leave, previous_applied_leave)
                            print("credited_leave ; crd ; previous_applied_leave : ",credited_leave, total_credited_leave, previous_applied_leave)
                            leave_balance = (Decimal(credited_leave) - Decimal(previous_applied_leave))
                            print("leave_balance 4442 : ", leave_balance)  

                            month_index = current_month.month
                            print("month_index 1 :", month_index)    
                            monthly_metrics["data"][0][month_index] = f"{total_applied_leave:.2f}"
                            monthly_metrics["data"][1][month_index] = "-"
                            monthly_metrics["data"][2][month_index] = f"{leave_balance:.2f}"   
                            assign_rule.appliedleaves = previous_applied_leave
                            assign_rule.leavebalance = leave_balance
                            assign_rule.save()
                            rule_days = 1

                    elif cRule.days <= 0 and cRule.leavename == "Comp Off":
                
                        compoff_count = CompOff.objects.filter(user=employee_id, punch_data__date__year=current_month.year, punch_data__date__month=current_month.month, punch_data__is_compoff_reverted=False).aggregate(total_cred=Sum('creditedleaves'))['total_cred']

                        print("compoff_count 4138:", employee_id)

                        if compoff_count is None:
                            compoff_count = 0
                        print("compoff_count: ", compoff_count)

                        total_credited_leave = compoff_count

                        canceled_request = 0
                        rejected_request = 0
                        # Query the Leave table for the employee's leaves within the current month
                        leave_data = Leave.objects.filter(
                            applicant_email_id=employee_id,
                            strtDate__lte=last_day_of_month,
                            endDate__gte=current_month
                        ).values('leavetyp', 'Days', 'strtDate', 'endDate').annotate(
                            applied_leave=Sum('Days'),
                            canceled_request=Sum(
                                Case(When(cancel_requested=True, then='Days'),
                                    default=0, output_field=IntegerField())
                            ),
                            rejected_request=Sum(
                                Case(When(rejected=True, then='Days'),
                                    default=0, output_field=IntegerField())
                            ),
                        )

                        applied_leave_dict = {leave_type: Decimal(
                            '0.00') for leave_type in assign_rule.rules_applied.all()}
                        print("applied_leave_dict :", applied_leave_dict)
                        total_applied_leave = Decimal('0.00')
                        days = Decimal('0.00')
                        print("DAYS :", days)

                        for data in leave_data:
                            applied_leavename = data['leavetyp']
                            print("NAME :", applied_leavename, cRule.leavename)
                            print("DATA : ", data)
                            if applied_leavename == cRule.leavename:
                                leave_type = data['leavetyp']
                                applied_leave = Decimal(data['applied_leave'] or '0.00')
                                applied_leave_dict[leave_type] = applied_leave
                                print("leave_type :", leave_type, "applied_leave :", applied_leave, "applied_leave_dict[leave_type] : ", applied_leave_dict[leave_type])

                                canceled_request += data['canceled_request']
                                rejected_request += data['rejected_request']
                                total_applied_leave += applied_leave
                                print("total_applied_leave :", total_applied_leave)

                                if rejected_request >= 1:
                                    days += Decimal(data['Days'])
                                    print("days: ", days)
                        
                        for leave_type in assign_rule.rules_applied.all().values_list('leavename', flat=True):

                            credited_leave = compoff_count
                            print("credited_leave 3000 : ", credited_leave)
                            applied_leave = applied_leave_dict.get(leave_type, Decimal('0.00'))
                            print("applied_leave : ", applied_leave)
                            previous_applied_leave += total_applied_leave
                            print("prev_appL : ", previous_applied_leave)

                            if applied_leave == Decimal('0.00'):
                                print("previous_credited_leave 3005 : ",
                                    previous_credited_leave)
                                credited_leave += previous_credited_leave
                                print("credited_leave 3006 : ", credited_leave)
                            else:
                                if rejected_request >= 1:
                                    credited_leave += previous_credited_leave
                                    total_applied_leave -= days
                                    previous_applied_leave -= days
                                    print("credited_leave 3011 : ", credited_leave,
                                        total_applied_leave, previous_applied_leave)
                                    # previous_applied_leave -= applied_leave
                                    # applied_leave -= applied_leave_dict[leave_type]
                                    # print("preapp :", previous_applied_leave, applied_leave)

                                else:
                                    #     previous_credited_leave -= applied_leave
                                    print("applied_leave :", applied_leave)
                                    print("previous_credited_leave 3017: ",
                                        previous_credited_leave)
                                    credited_leave += previous_credited_leave
                                    print("credited_leave 3016 : ", credited_leave)

                            print("credited_leave ; crd : ",
                                credited_leave, total_credited_leave)
                            leave_balance = (Decimal(credited_leave) - Decimal(previous_applied_leave))
                            print("leave_balance 3020 : ", leave_balance)

                            if applied_leave == Decimal('0.00'):
                                previous_credited_leave = credited_leave
                                print("previous_credited_leave 3023 : ",previous_credited_leave)
                            else:
                                previous_credited_leave = credited_leave
                                print("previous_credited_leave 3024 : ",previous_credited_leave)

                            print('leave_balance , credited_leave 3027: ',leave_balance, credited_leave)
                            # Find the index for the current month and update the data
                            month_index = current_month.month
                            print("month_index 1 :", month_index)
                            # monthly_metrics["data"][0][month_index] = f"{total_credited_leave:.2f}"
                            monthly_metrics["data"][0][month_index] = f"{total_credited_leave:.2f}"
                            monthly_metrics["data"][1][month_index] = f"{total_applied_leave:.2f}"
                            monthly_metrics["data"][2][month_index] = "-"
                            monthly_metrics["data"][3][month_index] = f"{leave_balance:.2f}"

                            assign_rule.creditedleaves = credited_leave
                            assign_rule.appliedleaves = previous_applied_leave
                            assign_rule.leavebalance = leave_balance
                            assign_rule.save()
                            rule_days = 1
                    
                    elif cRule.days <= 0 and cRule.leavename == "Loss Of Pay":
                        if cRule.leavename in assign_rule.rules_applied.all().values_list('leavename', flat=True):
                            leave_data = Leave.objects.filter(
                                leavetyp=cRule.leavename,
                                applicant_email_id=employee_id,
                                strtDate__lte=last_day_of_month,
                                endDate__gte=current_month
                            ).values('leavetyp').annotate(
                                applied_leave=Sum('Days'),
                                canceled_request=Sum(Case(
                                    When(cancel_requested=True, then=1), default=0, output_field=IntegerField())),
                                rejected_request=Sum(
                                    Case(When(rejected=True, then=1), default=0, output_field=IntegerField())),
                            )

                            print("leave_data 3060 : ", leave_data)

                            applied_leave_extract = leave_data.values_list(
                                'applied_leave', flat=True)
                            print("applied_leave_extract : ",
                                applied_leave_extract)
                            if applied_leave_extract.exists():
                                applied_leave_ = applied_leave_extract[0]
                                print("applied_leave_ 1: ", applied_leave_)
                            else:
                                applied_leave_ = 0
                                print("applied_leave_ 2: ", applied_leave_)

                            previous_applied_leave += applied_leave_
                            print("previous_applied_leave 4133:", previous_applied_leave)

                            penalty_count = PenaltyLogs.objects.filter(user=employee_id, punch_data__date__year=current_month.year, punch_data__date__month=current_month.month, punch_data__is_penalty_reverted=False).aggregate(total_deduction=Sum('deduction'))['total_deduction']

                            print("penalty_count 4138:", employee_id, penalty_count)

                            if penalty_count is None:
                                penalty_count = 0
                            print("penalty_count: ", penalty_count)

                            previous_penalty_count += penalty_count
                            month_index = current_month.month

                            print("month_index : ", month_index)

                            # Update only applied_leaves and penalty_deduction values
                            monthly_metrics["data"][1][month_index] = f"{applied_leave_:.2f}"
                            monthly_metrics["data"][2][month_index] = penalty_count
                            # assign_rule.creditedleaves = Decimal("0.00")
                            assign_rule.appliedleaves = previous_applied_leave
                            assign_rule.penaltydeduction = previous_penalty_count
                            # assign_rule.leavebalance = Decimal("0.00")
                            assign_rule.save()
                            rule_days = 0
                            print("applied_leave_ {}" f"{applied_leave_:.2f}")
                
                print("CFE :", cRule.CarryForwardeEnabled)
                # Move to the next month
                current_month = current_month.replace(day=1) + relativedelta(months=1)
                print("current_month : ", current_month)

            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

            if rule_days == 0:
                data = monthly_metrics
                column_names = data['column_name']
                data_rows = data['data']
                filtered_data = {'column_name': column_names, 'data': []}
                print("filtered_data : ", filtered_data)

                for row in data_rows:
                    if row[0] == 'Applied Leaves' or row[0] == 'Penalty Deduction':
                        filtered_data['data'].append(row)

                monthly_metrics = filtered_data
                print("monthly_metrics : ", monthly_metrics)
    
        print("SUCCESS")        

    print("SUCCESSFULY RUN")      
    return HttpResponse("SUCCESS")