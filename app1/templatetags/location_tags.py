from django import template
from django.core.cache import cache
from django.utils.timezone import make_aware
from app1.models import Punch, EmployeeGeoFence, EmployeeProfile
from datetime import datetime, timedelta
import pytz
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

register = template.Library()  # ✅ This line is required

@register.simple_tag
def get_clocked_in_location(user, selected_date=None):
    if not user or not hasattr(user, "id") or not user.id:
        return "Invalid User"

    if not selected_date:
        return "No Date Selected"

    try:
        # Timezone setup
        start_dt = datetime.combine(selected_date, datetime.min.time())
        end_dt = datetime.combine(selected_date + timedelta(days=1), datetime.min.time())

        # Get punch for selected date
        punch = Punch.objects.filter(user=user, date__gte=start_dt, date__lt=end_dt).first()
        if not punch:
            return "No Punch"

        if punch.WfhOrWfo == "WFH":
            try:
                geo = EmployeeGeoFence.objects.get(user=user)
                if geo.home_lat and geo.home_lon:
                    cache_key = f"location_{geo.home_lat}_{geo.home_lon}"
                    location_name = cache.get(cache_key)

                    if not location_name:
                        geolocator = Nominatim(user_agent="hrms-attendance")
                        location = geolocator.reverse((geo.home_lat, geo.home_lon), timeout=5)
                        location_name = location.address if location else "Unknown Location"
                        cache.set(cache_key, location_name, timeout=86400)

                    return f"WFH - {location_name}"
                else:
                    return "WFH - Location not set"
            except EmployeeGeoFence.DoesNotExist:
                return "WFH - No Home Location"

        elif punch.WfhOrWfo == "WFO":
            try:
                profile = EmployeeProfile.objects.get(user=user)
                return f"WFO - {profile.branch_location.name}" if profile.branch_location else "WFO - Not Assigned"
            except EmployeeProfile.DoesNotExist:
                return "WFO - No Branch Profile"

        else:
            return "Unknown Mode"

    except GeocoderTimedOut:
        return "Geolocation Timeout"
    except Exception as e:
        return f"Error: {str(e)}"
