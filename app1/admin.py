from django.contrib import admin
# Register your models here.
from django.db.models import Q
from .models import *
from django.contrib.sessions.models import Session
from .forms import *
from django.utils.safestring import mark_safe

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'email','status', 'admin_id']
    # def get_queryset(self, request):
    #     queryset = super(UserAdmin, self).get_queryset(request)
    #     admin_id = request.user.id
    #     return queryset.filter(Q(admin_id = admin_id)|Q(id = admin_id))


admin.site.register(Myprofile)
admin.site.register(Workhistory)
admin.site.register(Reportingmanager)
admin.site.register(Directreports)
admin.site.register(Educationalinfo)
admin.site.register(Familymembers)
admin.site.register(Emergencycontact)
admin.site.register(Uploadeddocs)
admin.site.register(Certifications)
admin.site.register(Work)
admin.site.register(Filemanager)
@admin.register(LeaveNotification)
class LeaveNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','message', 'timestamp']

admin.site.register(reimbursement)
admin.site.register(Runpayroll_lop)


@admin.register(companyprofile)
class companyprofileAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(companyprofileAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


@admin.register(companypolicy)
class companypolicyAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(companypolicyAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


@admin.register(corporateaddress)
class corporateaddressAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(corporateaddressAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


@admin.register(registeredaddress)
class registeredaddressAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(registeredaddressAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(DesignationAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(DepartmentAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


@admin.register(Subdepartment)
class SubdepartmentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(SubdepartmentAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(JobAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


admin.site.register(Leave)


admin.site.register(Clock)


@admin.register(Worklocation)
class WorklocationAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(WorklocationAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


admin.site.register(Email_config)
admin.site.register(AttendanceRule)
admin.site.register(Bank_account)


@admin.register(SalaryComponent)
class SalaryComponentAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(SalaryComponentAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


admin.site.register(SalaryStructureRule)

admin.site.register(SalaryStructureName)

admin.site.register(SalaryStructureAmount)

admin.site.register(AssignSalaryStructure)
admin.site.register(AssignSalaryStructureName)
admin.site.register(AssignSalaryStructureAmount)

admin.site.register(HolidayList)


admin.site.register(HolidayLocationList)

@admin.register(Workweek)
class WorkweekAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(WorkweekAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


@admin.register(CompanyRules)
class CompanyRulesAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        queryset = super(CompanyRulesAdmin, self).get_queryset(request)
        admin_id = request.user.id
        return queryset.filter(admin_id=admin_id)


admin.site.register(assignrule)
admin.site.register(ResignationForm)


@admin.register(Punch)
class PunchAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'user', 'status', 'first_clock_in_time', 'first_clock_out_time', 'second_clock_in_time', 'second_clock_out_time',  'is_first_clocked_in', 'is_first_clocked_out',
                    'punch_in_count', 'punch_out_count', 'is_shift_one', 'is_shift_two', 'break_count', 'in_time_anomaly', 'out_time_anomaly', 'work_duration_anomaly','is_requested','is_approved', 'last_punch_type', ]
    search_fields = ['id','user__email','user__id','user__username']

@admin.register(Proof)
class Admin(admin.ModelAdmin):
    list_display = ['id', 'proof_name']


@admin.register(AssignAttendanceRule)
class AssignAttendanceRuleAdmin(admin.ModelAdmin):

    list_display = ['user_id', 'rules_applied', 'effective_date']

admin.site.register(adhoc_earning)

admin.site.register(adhoc_deduction)

admin.site.register(Adhoc)

admin.site.register(PayRegister)

admin.site.register(PayActionStatus)

admin.site.register(PayoutStatus)

admin.site.register(AssignWorkWeek)
@admin.register(RequestApproval)
class RequestApprovalAdmin(admin.ModelAdmin):
    list_display = ['id' , 'user' , 'admin_id' , 'punch_data','in_time' , 'out_time','is_approved','is_rejected' , 'created_at', 'reason']


@admin.register(CompOff)
class CompOffAdmin(admin.ModelAdmin):
    list_display = ['id', 'user','punch_data', 'created_at']


@admin.register(PenaltyLogs)
class PenaltyLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'punch_data',
                    'get_punch_date', 'created_at', 'updated_at']
    search_fields = ['id','user__email','user__id','user__username']
    def get_punch_date(self, obj):
        return obj.punch_data.date if obj.punch_data else None

    get_punch_date.short_description = 'Punch Date'


# admin.site.register(Session)
@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = [
        "session_key",
        "expire_date",
        "session_data",
    ]

admin.site.register(WFOCount)

@admin.register(EmployeeGeoFence)
class EmployeeGeoFenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'home_lat', 'home_lon', 'home_radius')



@admin.register(CompanyBranchLocation)
class CompanyBranchLocationAdmin(admin.ModelAdmin):
    form = BranchLocationForm
    list_display = ('name', 'lat', 'lon', 'radius')

    class Media:
        js = (
            "https://maps.googleapis.com/maps/api/js?key=AIzaSyC1RHlyqpClD4e6WQQLujLCndKe5ab2n9k&callback=initMap",  # ✅ Replace with your actual key
        )
        css = {
            "all": ("admin/css/maps_widget.css",)
        }

    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        context['adminform'].form.fields['lat'].widget.attrs.update({'id': 'id_lat'})
        context['adminform'].form.fields['lon'].widget.attrs.update({'id': 'id_lon'})

        context['map_widget'] = mark_safe("""
            <div id="map" style="height: 400px; width: 100%; margin: 10px 0;"></div>
            <script>
              function initMap() {
                const latInput = document.getElementById('id_lat');
                const lonInput = document.getElementById('id_lon');

                const defaultLat = parseFloat(latInput.value) || 10.000000;
                const defaultLon = parseFloat(lonInput.value) || 76.000000;

                const map = new google.maps.Map(document.getElementById('map'), {
                  zoom: 14,
                  center: { lat: defaultLat, lng: defaultLon },
                });

                const marker = new google.maps.Marker({
                  position: { lat: defaultLat, lng: defaultLon },
                  map: map,
                  draggable: true
                });

                marker.addListener('dragend', function () {
                  const pos = marker.getPosition();
                  latInput.value = pos.lat().toFixed(8);
                  lonInput.value = pos.lng().toFixed(8);
                });
              }
            </script>
        """)
        return super().render_change_form(request, context, add, change, form_url, obj)


@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'branch_location', 'home_edit_requested')
    list_editable = ('branch_location',)
    search_fields = ['user__username', 'user__email']
