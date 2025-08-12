import datetime
from django.shortcuts import redirect, render
from datetime import datetime, timedelta, time
from dateutil import parser


def shopUserHome(request):

    if not request.user.is_authenticated:

        return render(request, 'login.html')

    else:

        role = request.user.role

        if role == "Employee":

            return redirect('empdash')

        elif role == "Admin":

            return redirect('dashboard')

        else:

            return render(request, 'login.html')


""" Time Delta converter """


def timedelta_from_datetime_or_time(input_time):
    # print("INPUT: ", input, type(input), end="\n\n")

    if isinstance(input_time, datetime):
        # print("datetime \n")
        return datetime.now() - input_time
    elif isinstance(input_time, time):
        # print("time \n")
        # Constructing timedelta directly from input time
        return timedelta(hours=input_time.hour, minutes=input_time.minute, seconds=input_time.second, microseconds=input_time.microsecond)
    else:
        raise TypeError(
            "Input must be either datetime.datetime or datetime.time")


""" Get Durations """


def get_half_hour(half_hour, half_minutes):
    half_day = timedelta(minutes=half_hour * 60 + half_minutes)
    return half_day


def get_work_duration(punch_object, current_time):

    if punch_object.is_first_clocked_in is True and punch_object.first_clock_in_time is not None:
        first_clocked_in_time = punch_object.first_clock_in_time
    else:
        first_clocked_in_time = time(hour=0, minute=0, second=0)

    if punch_object.is_first_clocked_out is True and punch_object.first_clock_out_time is not None:
        first_clocked_out_time = punch_object.first_clock_out_time
    else:
        first_clocked_out_time = time(hour=0, minute=0, second=0)

    first_clocked_in_time = datetime.strptime(
        str(first_clocked_in_time).split('.')[0], "%H:%M:%S").time()
    first_clocked_out_time = datetime.strptime(
        str(first_clocked_out_time).split('.')[0], "%H:%M:%S").time()

    if punch_object.is_first_clocked_in and punch_object.is_first_clocked_out:
        # print('First', first_clocked_in_time, first_clocked_out_time)
        work_duration = timedelta_from_datetime_or_time(
            first_clocked_out_time) - timedelta_from_datetime_or_time(first_clocked_in_time)
        # print("Function work duration: ", work_duration)
        return work_duration
    elif punch_object.is_first_clocked_in and not punch_object.is_first_clocked_out:
        # print('Second')
        work_duration = timedelta_from_datetime_or_time(
            current_time) - timedelta_from_datetime_or_time(first_clocked_in_time)
        return work_duration
    elif punch_object.is_first_clocked_in and punch_object.is_first_clocked_out and punch_object.is_second_clocked_in:
        # print('Third')
        work_duration = timedelta_from_datetime_or_time(
            current_time) - timedelta_from_datetime_or_time(first_clocked_in_time)
        return work_duration


def is_last_week_of_month(current_date):

    last_day_of_month = current_date.replace(
        day=1, month=current_date.month % 12+1) - timedelta(days=1)
    total_weeks = last_day_of_month.isocalendar()[1]
    return current_date.isocalendar()[1] == total_weeks

def parse_and_format_date(date_str):
    try:
        parsed_date = parser.parse(date_str)
    except ValueError:
        return None
    return parsed_date.strftime("%d %B %Y")


from math import radians, cos, sin, asin, sqrt

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two lat/lon coordinates using the Haversine formula."""
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    return R * c

def is_within_geofence(current_lat, current_lon, fence_lat, fence_lon, fence_radius):
    try:
        current_lat = float(current_lat)
        current_lon = float(current_lon)
        fence_lat = float(fence_lat)
        fence_lon = float(fence_lon)
        fence_radius = float(fence_radius)
    except (TypeError, ValueError) as e:
        print(f"❌ Invalid coordinates: {e}")
        return False

    distance = calculate_distance(current_lat, current_lon, fence_lat, fence_lon)

    print(f"📍 Current: ({current_lat}, {current_lon})")
    print(f"🎯 Target: ({fence_lat}, {fence_lon})")
    print(f"📏 Distance: {distance:.2f} meters")
    print(f"📐 Allowed Radius: {fence_radius:.2f} meters")

    return distance <= fence_radius


# Expeience Certificate
def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')