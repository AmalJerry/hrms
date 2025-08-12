from django import forms
from .models import *


class BranchLocationForm(forms.ModelForm):
    class Meta:
        model = CompanyBranchLocation
        fields = ['name', 'lat', 'lon', 'radius']



class EmployeeProfileCreateForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.filter(role='Employee', status__in=['Active', 'Onboarding']),
        label="Select Employee"
    )
    branch_location = forms.ModelChoiceField(
        queryset=CompanyBranchLocation.objects.all(),
        label="Assign Branch Location"
    )

    class Meta:
        model = EmployeeProfile
        fields = ['user', 'branch_location', 'home_edit_requested']
