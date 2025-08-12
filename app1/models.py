from datetime import datetime
import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from dateutil.relativedelta import relativedelta

from .utils import parse_and_format_date

class UserManager(BaseUserManager):

    def _create_user(self, phone, password, **other_fields):
        """
        Create and save a user with the given email and password. And any other fields, if specified.
        """
        if not phone:
            raise ValueError('Valid Mobile number must be given')

        user = self.model(phone=phone, **other_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def _create_user_phone(self, phone, password, otp, **other_fields):
        """
        Create and save a user with the given email and password. And any other fields, if specified.
        """
        if not phone:
            raise ValueError('Phone number is mandatory')

        user = self.model(phone=phone, password=password,
                          otp=otp, **other_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone, password=None, **other_fields):
        other_fields.setdefault('is_staff', False)
        other_fields.setdefault('is_superuser', False)
        return self._create_user(phone, password, **other_fields)

    def create_user_phone(self, phone, password, otp, **other_fields):
        other_fields.setdefault('is_staff', False)
        other_fields.setdefault('is_superuser', False)
        return self._create_user_phone(phone, password, otp, **other_fields)

    def create_superuser(self, phone, password=None, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone, password, **other_fields)


class User(AbstractUser):
    roles = (
        ('Admin', 'Admin'),
        ('Employee', 'Employee')
    )
    choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Transgender', 'Transgender'),
    )
    STATUS = (
        ('Onboarding', 'Onboarding'),
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )
    type = {
        ('Full Time', 'Full Time'),
        ('Part Time', 'Part Time'),
        ('Intern', 'Intern'),
        ('Contract', 'Contract')
    }
    role = models.CharField(
        max_length=50, choices=roles, null=True, blank=True)
    admin_id = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=50, unique=True)
    phone = models.CharField(max_length=20, null=True)
    image = models.ImageField(upload_to="Photos/", null=True)
    dob = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(
        max_length=50, choices=choices, null=True, blank=True)
    empid = models.IntegerField(null=True)
    emptype = models.CharField(
        max_length=40, choices=type, null=True, blank=True)
    probperiod = models.CharField(max_length=40, null=True, blank=True)
    reptmgr = models.ForeignKey(
        'self', on_delete=models.CASCADE, blank=True, null=True)
    department = models.ForeignKey(
        'Department', on_delete=models.SET_NULL, null=True, blank=True)
    designation = models.ForeignKey(
        'Designation', on_delete=models.SET_NULL, null=True, blank=True)
    subdepartment = models.ForeignKey(
        'Subdepartment', on_delete=models.SET_NULL, blank=True, null=True)
    jobtitle = models.ForeignKey(
        'Job', on_delete=models.SET_NULL, null=True, blank=True)
    wrklcn = models.ForeignKey('Worklocation', on_delete=models.SET_NULL, null=True, blank=True)
    company_type = models.ForeignKey(
        'CompanyProfile', on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(
        max_length=50, choices=STATUS, null=True, blank=True)
    # company_type=models.ForeignKey('Companyprofile',on_delete=models.SET_NULL, null=True, blank=True)
    wrkexp = models.CharField(max_length=50, null=True, blank=True)
    datejoin = models.CharField(max_length=50, null=True, blank=True)
    otp = models.CharField(max_length=100, null=True, default=None)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone', 'username', 'role',
                       'status', 'password', 'otp', 'empid']

    objects = UserManager()

    def get_username(self):
        return str(self.email)
    
    def is_birthday_today(self):
        today = datetime.now().date()

        if self.dob:
            dob_date = datetime.strptime(parse_and_format_date(self.dob), '%d %B %Y').date()
            return dob_date.month == today.month and dob_date.day == today.day
        return False
    
    def is_workanniversary_today(self):
        today = datetime.now().date()

        if self.datejoin:
            date_join = datetime.strptime(parse_and_format_date(self.datejoin), '%d %B %Y').date()
            years_of_service = relativedelta(today, date_join).years
            return date_join.month == today.month and date_join.day == today.day and years_of_service >= 1
        return False

class ResignationForm(models.Model):

    Reasons = (
        ('Resignation', 'Resignation'),
        ('Retirement', 'Retirement'),
        ('End of Contract', 'End of Contract'),
        ('Voluntary Separation', 'Voluntary Separation'),
        ('Termination', 'Termination'),
        ('Layoff', 'Layoff'),
        ('Relocation', 'Relocation'),
        ('Career Change', 'Career Change'),
        ('Personal Reasons', 'Personal Reasons'),
        ('Promotion/Internal Transfer', 'Promotion/Internal Transfer'),
        ('Higher Education Pursuit', 'Higher Education Pursuit'),
        ('Health Issues', 'Health Issues'),
        ('Family Responsibilities', 'Family Responsibilities'),
        ('Company Restructuring', 'Company Restructuring'),
        ('Dissatisfaction with the Work Environment',
         'Dissatisfaction with the Work Environment'),
        ('Unfulfilled Growth Opportunities', 'Unfulfilled Growth Opportunities'),
        ('Change in the Job Market', 'Change in the Job Market'),
        ('Entrepreneurship/Starting Own Business',
         'Entrepreneurship/Starting Own Business'),
        ('Job Redundancy', 'Job Redundancy'),
        ('End of Project/Contract Completion',
         'End of Project/Contract Completion'),
        ('Others', 'Others'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Updated', 'Updated'),
    )

    user = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True)
    resignation_date = models.DateField(null=True, blank=True)
    reason = models.CharField(
        max_length=500, choices=Reasons, null=True, blank=True)
    actual_last_working_day = models.DateField(null=True, blank=True)
    last_workingday = models.DateField(null=True, blank=True)
    notice_period = models.IntegerField(null=True)
    Shortfall = models.IntegerField(null=True)
    resignation_letter = models.CharField(
        max_length=1000, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending', null=True, blank=True)
    cancel_requested = models.BooleanField(default=False)
    rejection_reason = models.CharField(max_length=500, null=True, blank=True)
    update_message = models.TextField(null=True, blank=True)
    allow_edit = models.BooleanField(default=False)


class Leave(models.Model):
    leavetyp = models.CharField(max_length=50, null=True, blank=True)
    leavename = models.ForeignKey(
        'assignrule', on_delete=models.SET_NULL, null=True, blank=True)
    strtDate = models.DateField(null=True, blank=True)
    Selecthalf1 = models.CharField(max_length=50, null=True, blank=True)
    endDate = models.DateField(null=True, blank=True)
    Selecthalf2 = models.CharField(max_length=50, null=True, blank=True)
    Reason = models.CharField(max_length=1500, null=True, blank=True)
    Appliedon = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    Days = models.FloatField(null=True, blank=True)
    cancel_requested = models.BooleanField(default=False)
    applicant_email = models.ForeignKey(
        'User', on_delete=models.SET_NULL, null=True, blank=True)
    rejection_reason = models.CharField(max_length=100, null=True, blank=True)
    rejected = models.BooleanField(default=False)
    useremail = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    admin_id = models.IntegerField(max_length=50, null=True, blank=True)
    punch_data = models.ForeignKey("Punch", null=True, on_delete=models.SET_NULL)
    created_date = models.DateTimeField(
        null=True, auto_now=True, auto_now_add=False)
    

    def __str__(self):
        return self.leavetyp
      
class Runpayroll_lop(models.Model):
    lop_count = models.FloatField(null=True, blank=True)
    user_id = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    lop_date = models.DateTimeField(null=True, auto_now=False, auto_now_add=False)

class Myprofile(models.Model):
    Marital = (
        ('Single', 'Single'),
        ('Maried', 'Maried'),
        ('Divorced', 'Divorced'),
        ('Widowed', 'Widowed')
    )

    bldgrp = models.CharField(max_length=50, null=True, blank=True)
    marital = models.CharField(
        max_length=40, choices=Marital, null=True, blank=True)
    image = models.ImageField(upload_to="Photos/", null=True, blank=True)
    offemail = models.EmailField(max_length=50, null=True, blank=True)
    altphone = models.CharField(max_length=20, null=True, blank=True, help_text="Store phone number as string to preserve formatting, leading zeros, or country codes")
    address = models.CharField(max_length=300, null=True, blank=True)
    peraddress = models.CharField(max_length=300, null=True, blank=True)
    housetype = models.CharField(max_length=50, null=True, blank=True)
    crntresidencedate = models.CharField(max_length=50, null=True, blank=True)
    crntcitydate = models.CharField(max_length=50, null=True, blank=True)
    myuser = models.ForeignKey("User", on_delete=models.CASCADE, null=True)

    # workhistory
class Workhistory(models.Model):
    myuser_1 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    dep1 = models.CharField(max_length=50, null=True, blank=True)
    design1 = models.CharField(max_length=50, null=True, blank=True)
    from_date = models.CharField(max_length=50, null=True, blank=True)
    to_date = models.CharField(max_length=50, null=True, blank=True)

    # reportingmanager
class Reportingmanager(models.Model):
    types = {
        ('Primary', 'Primary'),
        ('Secondary', 'Secondary'),
    }
    myuser_2 = models.ManyToManyField("User")
    userid = models.IntegerField(null=True)
    type = models.CharField(max_length=40, choices=types, null=True, blank=True)

    # directreportsz
class Directreports(models.Model):
    myuser_3 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    admin_id = models.IntegerField(null=True)
    name2 = models.CharField(max_length=100, null=True, blank=True)
    dept3 = models.ForeignKey(
        'Department', on_delete=models.SET_NULL, null=True, blank=True)
    design3 = models.ForeignKey(
        'Designation', on_delete=models.SET_NULL, null=True, blank=True)
    
    # educationalinfo
class Educationalinfo(models.Model):
    myuser_4 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    qualification = models.CharField(max_length=50, null=True, blank=True)
    course = models.CharField(max_length=500, null=True, blank=True)
    institute = models.CharField(max_length=300, null=True, blank=True)
    passout = models.CharField(max_length=50, null=True, blank=True)
    percent = models.CharField(max_length=50, null=True, blank=True)

    # familymembers
class Familymembers(models.Model):
    myuser_5 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    name3 = models.CharField(max_length=100, null=True, blank=True)
    relation = models.CharField(max_length=50, null=True, blank=True)
    dob1 = models.CharField(max_length=50, null=True, blank=True)
    dependant = models.CharField(max_length=50, null=True, blank=True)

    # emergencycontact
class Emergencycontact(models.Model):
    myuser_6 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    name4 = models.CharField(max_length=100, null=True, blank=True)
    relation1 = models.CharField(max_length=50, null=True, blank=True)
    phone1 = models.CharField(max_length=20, null=True, blank=True)


class Proof(models.Model):
    proof_name = models.CharField(max_length=50, null=True)
    admin_id = models.IntegerField(null=True, blank=True)

    # uploadeddocs
class Uploadeddocs(models.Model):
    myuser = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    type1 = models.CharField(max_length=50, null=True, blank=True)
    id_no = models.CharField(max_length=20, null=True, blank=True)
    uploadedby = models.CharField(max_length=100, null=True, blank=True)
    verificationstatus = models.CharField(
        max_length=100, null=True, blank=True)
    image1 = models.ImageField(upload_to="Photos/", null=True, blank=True)
    proof = models.ManyToManyField(Proof)

    # certifications
class Certifications(models.Model):
    myuser_8 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    coursetitle = models.CharField(max_length=100, null=True, blank=True) # Course Type
    uploadedby1 = models.CharField(max_length=100, null=True, blank=True)
    type2 = models.CharField(max_length=500, null=True, blank=True) # Certificate Title
    verification = models.CharField(max_length=100, null=True, blank=True)
    image2 = models.FileField(upload_to="Photos/", max_length=255, null=True, blank=True)

    # work
class Work(models.Model):
    myuser_9 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    name5 = models.CharField(max_length=100, null=True, blank=True)
    uploadedby2 = models.CharField(max_length=100, null=True, blank=True)
    uploadedon = models.CharField(max_length=50, null=True, blank=True)
    description1 = models.CharField(max_length=200, null=True, blank=True)
    image3 = models.ImageField(upload_to="Photos/", max_length=255, null=True, blank=True)

    # filemanager
class Filemanager(models.Model):
    myuser_10 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    requesttype = models.CharField(max_length=50, null=True, blank=True)
    frmt = models.CharField(max_length=50, null=True, blank=True)
    scheduleon = models.DateTimeField(max_length=50, null=True, blank=True)
    size = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50, null=True, blank=True)
    saveexcel = models.FileField(upload_to="csv/", max_length=255, null=True, blank=True)


class companyprofile(models.Model):
    admin_id = models.IntegerField(null=True)
    registeredcompanyname = models.CharField(
        max_length=40, null=True, blank=True)
    brandname = models.CharField(max_length=100, null=True, blank=True)
    website = models.CharField(max_length=100, null=True, blank=True)
    domain = models.CharField(max_length=100, null=True, blank=True)
    fb = models.CharField(max_length=100, null=True, blank=True)
    twitter = models.CharField(max_length=100, null=True, blank=True)
    linkedin = models.CharField(max_length=100, null=True, blank=True)
    logo = models.ImageField(upload_to="Photos/", max_length=255, null=True, blank=True)
    inverse_logo = models.ImageField(upload_to="Photos/", max_length=255, null=True, blank=True)
    type_of_company = models.CharField(
        max_length=50,
        choices=[('Main Company', 'Main Company'), ('Sub Company', 'Sub Company')],
        default='Main Company'
    )

class registeredaddress(models.Model):
    admin_id = models.IntegerField(null=True)
    regofficeaddress = models.CharField(max_length=150, null=True, blank=True)
    regpincode = models.IntegerField(max_length=10, null=True, blank=True)
    regdistrict = models.CharField(max_length=40, null=True, blank=True)
    regstate = models.CharField(max_length=40, null=True, blank=True)
    regcountry = models.CharField(max_length=40, null=True, blank=True)


class corporateaddress(models.Model):
    admin_id = models.IntegerField(null=True)
    corpofficeaddress = models.CharField(max_length=150, null=True, blank=True)
    corppincode = models.IntegerField(max_length=10, null=True, blank=True)
    corpdistrict = models.CharField(max_length=40, null=True, blank=True)
    corpstate = models.CharField(max_length=40, null=True, blank=True)
    corpcountry = models.CharField(max_length=40, null=True, blank=True)


class companypolicy(models.Model):
    admin_id = models.IntegerField(null=True)
    companypolicies = models.CharField(max_length=100, null=True, blank=True)
    policydoc = models.FileField(upload_to="Photos/", max_length=255, null=True, blank=True)

class Designation(models.Model):
    admin_id = models.IntegerField(null=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

class Department(models.Model):
    admin_id = models.IntegerField(null=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name

class Subdepartment(models.Model):
    admin_id = models.IntegerField(null=True)
    depname = models.ForeignKey(
        Department, on_delete=models.CASCADE, null=True, blank=True)
    subname = models.CharField(max_length=40, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.subname

class Job(models.Model):
    admin_id = models.IntegerField(null=True)
    name = models.CharField(max_length=50, null=True, blank=True)

class Worklocation(models.Model):
    admin_id = models.IntegerField(null=True)
    location = models.CharField(max_length=100, null=True, blank=True)

class CompanyRules(models.Model):
    MONTHS = (
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December')
    )

    admin_id = models.IntegerField(null=True)
    leavename = models.CharField(max_length=25, null=True, blank=True)
    description = models.CharField(max_length=1000, null=True, blank=True)
    days = models.IntegerField(null=True, blank=True)
    applicability = models.CharField(max_length=20, null=True, blank=True)
    carryforward = models.CharField(max_length=20, null=True, blank=True)

    WeekendsBWLeave = models.CharField(max_length=100, null=True, blank=True)
    HolidaysBWLeave = models.CharField(max_length=100, null=True, blank=True)
    CreditableAccrual = models.CharField(max_length=100, null=True, blank=True)
    AccrualFrequency = models.CharField(max_length=100, null=True, blank=True)
    AccrualPeriod = models.CharField(max_length=100, null=True, blank=True)
    AllowedUnderProbation = models.CharField(
        max_length=100, null=True, blank=True)
    AllowedUnderNoticePeriod = models.CharField(
        max_length=100, null=True, blank=True)
    CarryForwardeEnabled = models.CharField(
        max_length=100, null=True, blank=True)
    LeaveEncashEnabled = models.CharField(
        max_length=100, null=True, blank=True)
    AllLeaveEncashable = models.CharField(
        max_length=100, null=True, blank=True)
    MaxLeaveEncashable = models.CharField(
        max_length=100, null=True, blank=True)

    MaxLeavesAllowed = models.CharField(max_length=100, null=True, blank=True)
    ContinuousLeavesAllowed = models.CharField(
        max_length=100, null=True, blank=True)
    NegativeLeavesAllowed = models.CharField(
        max_length=100, null=True, blank=True)
    FutureDatedLeavesAllowed = models.CharField(
        max_length=100, null=True, blank=True)
    FutureDatedLeavesAllowedAfter = models.CharField(
        max_length=100, null=True, blank=True)
    BackdatedLeavesAllowed = models.CharField(
        max_length=100, null=True, blank=True)
    BackdatedLeavesAllowedUpTo = models.CharField(
        max_length=100, null=True, blank=True)
    ApplyLeavesforNextYearTill = models.CharField(
        max_length=40, choices=MONTHS, null=True, blank=True)

    def __str__(self):
        return self.leavename

class Clock(models.Model):
    myuser_11 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    dte = models.DateField(max_length=200, null=True, blank=True)
    tym = models.TimeField(max_length=200, null=True, blank=True)

class Email_config(models.Model):
    email = models.EmailField(max_length=50, null=True, blank=True)
    password = models.CharField(max_length=50, null=True, blank=True)
    username = models.CharField(max_length=50, null=True, blank=True)
    designation = models.CharField(max_length=50, null=True, blank=True)
    c_name = models.CharField(max_length=50, null=True, blank=True)
    module = models.CharField(max_length=50, null=True, blank=True)

# Attendance models
class AttendanceRule(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    rulename = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=300, null=True, blank=True)
    # Shift Timings :
    inTime = models.TimeField(max_length=50, null=True, blank=True)
    outTime = models.TimeField(max_length=50, null=True, blank=True)
    enable_AD = models.BooleanField(default=False)
    autoDeductionDate = models.CharField(max_length=100, null=True, blank=True)
    enable_AT = models.BooleanField(default=False)
    # Anomaly Settings :
    inGracePeriod = models.TimeField(
        max_length=50, null=True, blank=True) 
    outGracePeriod = models.TimeField(
        max_length=50, null=True, blank=True) 
    fullhours = models.IntegerField(
        max_length=50, null=True, blank=True) 
    fullminutes = models.IntegerField(max_length=50, null=True, blank=True)
    halfhours = models.IntegerField(max_length=50, null=True, blank=True)
    halfminutes = models.IntegerField(
        max_length=50, null=True, blank=True)  

    maximum_TBD = models.BooleanField(default=False)
    maximum_NOB = models.BooleanField(default=False)
    auto_CO = models.BooleanField(default=False)

    enable_OT = models.BooleanField(default=False)
    enable_IR = models.BooleanField(default=False)
    enable_AWS = models.BooleanField(default=False)
    enable_CO = models.BooleanField(default=False)
    enable_PR = models.BooleanField(default=False)
    in_Time = models.BooleanField(default=False)
    lateComingAllowded = models.IntegerField(null=True, blank=True)
    penaltyInterval = models.IntegerField(null=True, blank=True)
    PENALTY = (
        ('Half Day', 'Half Day'),
        ('Full Day', 'Full Day'),)
    penalty = models.CharField(
        max_length=50, choices=PENALTY, null=True, blank=True)
    leaveDeduction = models.CharField(max_length=50, null=True, blank=True)

    # Out Time :-
    out_Time = models.BooleanField(default=False)
    earlyLeavingAllowded = models.IntegerField(null=True, blank=True)
    penaltyInterval1 = models.IntegerField(null=True, blank=True)
    PENALTY1 = (
        ('Half Day', 'Half Day'),
        ('Full Day', 'Full Day'),)
    penalty1 = models.CharField(
        max_length=50, choices=PENALTY, null=True, blank=True)
    leaveDeduction1 = models.CharField(max_length=50, null=True, blank=True)

    # Work Duration :-
    work_duration = models.BooleanField(default=False)
    ShortfallInWDAllowed = models.IntegerField(null=True, blank=True)
    penaltyInterval2 = models.IntegerField(null=True, blank=True)
    PENALTY2 = (
        ('Half Day', 'Half Day'),
        ('Full Day', 'Full Day'),)
    penalty2 = models.CharField(
        max_length=50, choices=PENALTY, null=True, blank=True)
    leaveDeduction2 = models.CharField(max_length=50, null=True, blank=True)


class AssignAttendanceRule(models.Model):
    user_id = models.ForeignKey(
        'User', on_delete=models.SET_NULL, blank=True, null=True)
    rules_applied = models.ForeignKey(
        'AttendanceRule', on_delete=models.SET_NULL, blank=True, null=True)
    effective_date = models.CharField(max_length=30, null=True, blank=True)


class assignrule(models.Model):
    user_id = models.ForeignKey(
        'User', on_delete=models.SET_NULL, blank=True, null=True)
    rules_applied = models.ManyToManyField(CompanyRules)
    effective_date = models.CharField(max_length=30, null=True, blank=True)
    creditedleaves = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    appliedleaves = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    penaltydeduction = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)
    leavebalance = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        name = str(self.user_id)
        leave_name =  str(self.rules_applied.all().values_list('leavename', flat=True)[0])
        penlty = str(self.penaltydeduction)
        leavebalance = str(self.leavebalance)

        return f"{name} {leave_name} penltydeduction = {penlty} and leavebalace = {leavebalance}"
    
class Bank_account(models.Model):
    myuser_11 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    account_holder_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=30, null=True, blank=True)
    bank_name = models.CharField(max_length=30, null=True, blank=True)
    branch_name = models.CharField(max_length=30, null=True, blank=True)
    IFSC_code = models.CharField(max_length=30, null=True, blank=True)
    city = models.CharField(max_length=30, null=True, blank=True)
    esa = models.CharField(max_length=30, null=True, blank=True)
    pfnum = models.CharField(max_length=30, null=True, blank=True)

# Salary component
class SalaryComponent(models.Model):
    admin_id = models.IntegerField(null=True)
    componentname = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=200, null=True, blank=True)
    Parentcomponentname = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    percent = models.FloatField(null=True, blank=True) 

    def _str_(self):
        return self.componentname

class SalaryStructureRule(models.Model):
    myuser_12 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    rule_name = models.CharField(max_length=100, null=True, blank=True)
    Description = models.CharField(max_length=700, null=True, blank=True)

class SalaryStructureName(models.Model):
    salaryrule = models.ForeignKey("SalaryStructureRule", on_delete=models.CASCADE, null=True)
    salarycomponent = models.ManyToManyField("SalaryComponent")

class SalaryStructureAmount(models.Model):
    amount = models.PositiveIntegerField(null=True, blank=True)
    salaryname = models.ForeignKey("SalaryStructureName", on_delete=models.CASCADE, null=True)

class AssignSalaryStructure(models.Model):
    user_id = models.ForeignKey('User', on_delete=models.SET_NULL, blank=True, null=True)
    assign_salary = models.ForeignKey('SalaryStructureRule', on_delete=models.SET_NULL, blank=True, null=True)
    effective_date = models.DateTimeField(max_length=30, null=True, blank=True)
    
class AssignSalaryStructureName(models.Model):
    salaryrule = models.ForeignKey("AssignSalaryStructure", on_delete=models.CASCADE, null=True)
    salarycomponent = models.ManyToManyField("SalaryComponent")

class AssignSalaryStructureAmount(models.Model):
    amount = models.PositiveIntegerField(null=True, blank=True)
    salaryname = models.ForeignKey("AssignSalaryStructureName", on_delete=models.CASCADE, null=True)

class Workweek(models.Model):
    admin_id = models.IntegerField(null=True, blank=True)
    off_day = models.CharField(max_length=50, null=True, blank=True)
    description = models.CharField(max_length=500, null=True, blank=True)
    rule_name = models.CharField(max_length=100, null=True, blank=True)
    half_day = models.CharField(max_length=100, null=True, blank=True)
    day_1 = models.CharField(max_length=50, null=True, blank=True)
    day_2 = models.CharField(max_length=50, null=True, blank=True)
    day_3 = models.CharField(max_length=50, null=True, blank=True)
    day_4 = models.CharField(max_length=50, null=True, blank=True)
    day_5 = models.CharField(max_length=50, null=True, blank=True)
    day_6 = models.CharField(max_length=50, null=True, blank=True)
    day_7 = models.CharField(max_length=50, null=True, blank=True)
    day_8 = models.CharField(max_length=50, null=True, blank=True)
    day_9 = models.CharField(max_length=50, null=True, blank=True)
    day_10 = models.CharField(max_length=50, null=True, blank=True)
    day_11 = models.CharField(max_length=50, null=True, blank=True)
    day_12 = models.CharField(max_length=50, null=True, blank=True)
    day_13 = models.CharField(max_length=50, null=True, blank=True)
    day_14 = models.CharField(max_length=50, null=True, blank=True)
    day_15 = models.CharField(max_length=50, null=True, blank=True)
    day_16 = models.CharField(max_length=50, null=True, blank=True)
    day_17 = models.CharField(max_length=50, null=True, blank=True)
    day_18 = models.CharField(max_length=50, null=True, blank=True)
    day_19 = models.CharField(max_length=50, null=True, blank=True)
    day_20 = models.CharField(max_length=50, null=True, blank=True)
    day_21 = models.CharField(max_length=50, null=True, blank=True)
    day_22 = models.CharField(max_length=50, null=True, blank=True)
    day_23 = models.CharField(max_length=50, null=True, blank=True)
    day_24 = models.CharField(max_length=50, null=True, blank=True)
    day_25 = models.CharField(max_length=50, null=True, blank=True)
    day_26 = models.CharField(max_length=50, null=True, blank=True)
    day_27 = models.CharField(max_length=50, null=True, blank=True)
    day_28 = models.CharField(max_length=50, null=True, blank=True)
    day_29 = models.CharField(max_length=50, null=True, blank=True)
    day_30 = models.CharField(max_length=50, null=True, blank=True)
    day_31 = models.CharField(max_length=50, null=True, blank=True)
    day_32 = models.CharField(max_length=50, null=True, blank=True)
    day_33 = models.CharField(max_length=50, null=True, blank=True)
    day_34 = models.CharField(max_length=50, null=True, blank=True)
    day_35 = models.CharField(max_length=50, null=True, blank=True)


class AssignWorkWeek(models.Model):
    user_id = models.ForeignKey(
        'User', on_delete=models.SET_NULL, blank=True, null=True)
    rules_applied = models.ForeignKey(
        'Workweek', on_delete=models.SET_NULL, blank=True, null=True)
    effective_date = models.CharField(max_length=30, null=True, blank=True)


class Punch(models.Model):
    STATUS = (
        ("P", "Present"),
        ("A", "Absent"),
        ("L", "Leave"),
        ("WO", "Weekly off"),
        ("H", "Holiday"),
        ("HL", "Half day leave"),
        ("AN", "Anomaly"),
        ("AC", "Auto Clock-out"),
    )

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    first_clock_in_time = models.TimeField(
        auto_now_add=False, null=True, blank=True)
    first_clock_out_time = models.TimeField(
        auto_now_add=False, null=True, blank=True)
    second_clock_in_time = models.TimeField(
        auto_now_add=False, null=True, blank=True)
    second_clock_out_time = models.TimeField(
        auto_now_add=False, null=True, blank=True)
    is_first_clocked_in = models.BooleanField(default=False)
    is_first_clocked_out = models.BooleanField(default=False)
    is_second_clocked_in = models.BooleanField(default=False)
    is_second_clocked_out = models.BooleanField(default=False)
    break_duration = models.TimeField(null=True, default="00:00:00")
    work_duration = models.TimeField(null=True, default="00:00:00")
    overtime = models.TimeField(null=True, default="00:00:00")
    punch_in_count = models.IntegerField(default=0)
    punch_out_count = models.IntegerField(default=0)
    is_shift_one = models.BooleanField(default=False)
    is_shift_two = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now=False, auto_now_add=False, null=True)
    last_punch_type = models.IntegerField(default=1)
    ip_address = models.GenericIPAddressField(default="12.0.0.1", null=True)
    location = models.CharField(
        max_length=50, null=True, default="Do not punch from mobile"
    )
    break_count = models.IntegerField(default=0, null=True)
    status = models.CharField(max_length=50, choices=STATUS, null=True)
    in_time_anomaly = models.BooleanField(default=False)
    out_time_anomaly = models.BooleanField(default=False)
    work_duration_anomaly = models.BooleanField(default=False)
    is_week_work = models.BooleanField(default=False)
    is_holiday_work = models.BooleanField(default=False)
    is_requested = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_penalty_reverted = models.BooleanField(default=False)
    is_compoff_reverted = models.BooleanField(default=False)
    is_penalty = models.BooleanField(default=False) # to filter none penalty objects from Punch table generate penalty log in automation log 
    WfhOrWfo = models.CharField(max_length=50, null=True, blank=True)
    
    def __str__(self):
        return str(self.id)+ " " +str(self.user) + " " +str(self.date)

class WFOCount(models.Model):
    wfocount = models.FloatField(null=True, blank=True)
    user_id = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, blank=True)
    wfo_date = models.DateTimeField(null=True, auto_now=False, auto_now_add=False)
    
class LeaveNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=555)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    admin_id = models.IntegerField(default=0, null=True)
    readadmin = models.BooleanField(default=False)
    readuser = models.BooleanField(default=False)
    events = models.IntegerField(default=0, null=True)

class HolidayList(models.Model):
    Myuser_13 = models.ForeignKey("User", on_delete=models.CASCADE)
    HolidayName = models.CharField(max_length=50, null=True, blank=True)
    HolidayDate = models.CharField(max_length=50, null=True, blank=True)

    def get_formatted_date(self):
        # Assuming HolidayDate is in the format "[27 November 2023]"
        date_str = self.HolidayDate.strip("[]")
        date_obj = datetime.strptime(date_str, "%d %B %Y")
        return date_obj.strftime("%Y-%m-%d")

class HolidayLocationList(models.Model):
    Holiday_List = models.ForeignKey(
        HolidayList, on_delete=models.CASCADE, null=True)
    HolidayLocation = models.ManyToManyField(Worklocation)
    HolidayToggleBtn_ON = models.CharField(
        max_length=50, null=True, blank=True)


class reimbursement(models.Model):
    myuser_11 = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    component = models.CharField(
        max_length=50, null=True, blank=True)
    STATUS = (
        ('Approved', 'Approved'),
        ('Pending', 'Pending'),
    )
    declared_amount = models.IntegerField(null=True, blank=True)
    document = models.FileField(upload_to='media/', max_length=255, null=True, blank=True)
    comment = models.CharField(max_length=500, null=True, blank=True)
    status = models.CharField(
        max_length=50, choices=STATUS, null=True, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True)

class adhoc_earning(models.Model):
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    component_name = models.CharField(max_length=50, null=True, blank=True)

class adhoc_deduction(models.Model):
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    component_name = models.CharField(max_length=50, null=True, blank=True)

class Adhoc(models.Model):
    type = {
        ('Earning', 'Earning'),
        ('Deduction', 'Contract')
    }
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    adhocearning = models.ForeignKey('adhoc_earning', on_delete=models.SET_NULL, null=True, blank=True)
    adhocdeduction = models.ForeignKey('adhoc_deduction', on_delete=models.SET_NULL, null=True, blank=True)
    cmptype = models.CharField(max_length=40, choices=type, null=True, blank=True)
    amount = models.PositiveIntegerField(null=True, blank=True)
    adminid = models.IntegerField(null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)

class PayRegister(models.Model):
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    netpay = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=40, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)

class PayActionStatus(models.Model):
    action = {
        ('Pay', 'Pay'),
        ('On Hold', 'On Hold')
    }
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    actiontype = models.CharField(max_length=40, choices=action, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)

class PayoutStatus(models.Model):
    STATUS = {
        ('Pay', 'Pay'),
        ('Unpaid', 'Unpaid')
    }
    user_id = models.ForeignKey("User", on_delete=models.CASCADE, null=True)
    status = models.CharField(max_length=40, choices=STATUS, null=True, blank=True)
    createddate = models.DateTimeField(null=True, blank=True)
    reason = models.CharField(max_length=1000, choices=STATUS, null=True, blank=True)

class RequestApproval(models.Model):
    user = models.ForeignKey("User", null=True, on_delete=models.SET_NULL)
    admin_id = models.IntegerField(null=True)
    punch_data = models.ForeignKey("Punch", null=True, on_delete=models.SET_NULL)
    org_in_time = models.TimeField(null=True, auto_now=False, auto_now_add=False)
    org_out_time = models.TimeField(null=True, auto_now=False, auto_now_add=False)
    in_time = models.TimeField(null=True, auto_now=False, auto_now_add=False)
    out_time = models.TimeField(null=True, auto_now=False, auto_now_add=False)
    reason = models.TextField(null=True) 
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    request_type = models.IntegerField(null=True)
    created_at = models.DateField(null=True, auto_now=True, auto_now_add=False)

class CompOff(models.Model):
    user = models.ForeignKey("User",  on_delete=models.SET_NULL, null=True)
    punch_data = models.ForeignKey("Punch", on_delete=models.SET_NULL, null= True)
    creditedleaves = models.DecimalField(max_digits=10, decimal_places=2, null=True) 
    created_at =models.DateField(auto_now=True, auto_now_add=False)

    def __str__(self) -> str:
        return str(self.user)+" "+ str(self.punch_data)
    
class PenaltyLogs(models.Model):
    user = models.ForeignKey("User", null=True, on_delete=models.SET_NULL)
    punch_data = models.ForeignKey("Punch", null=True, on_delete=models.SET_NULL)
    anomaly_type = models.CharField(null=True, max_length=50)
    penalty_type = models.CharField(null=True, max_length=50)
    leave_type = models.CharField(null=True, max_length=50)
    deduction = models.CharField(null=True, max_length=50)
    month = models.CharField(null=True, max_length=50)
    created_at = models.DateField(auto_now=True, auto_now_add=False)
    updated_at = models.DateField(auto_now=False, auto_now_add=True)

    def __str__(self) -> str:
        return str(self.user) + " || "+ str(self.punch_data) + "\n"




class EmployeeGeoFence(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    home_lat = models.DecimalField(max_digits=11, decimal_places=8)
    home_lon = models.DecimalField(max_digits=11, decimal_places=8)
    home_radius = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    updated_at = models.DateTimeField(auto_now=True)

class CompanyBranchLocation(models.Model):
    name = models.CharField(max_length=200)
    lat = models.DecimalField(max_digits=15, decimal_places=8)
    lon = models.DecimalField(max_digits=15, decimal_places=8)
    radius = models.DecimalField(max_digits=10, decimal_places=2, default=100) 

    def __str__(self):
        return self.name


class EmployeeProfile(models.Model):
    user = models.OneToOneField('User', on_delete=models.CASCADE, limit_choices_to={'role': 'Employee'})
    branch_location = models.ForeignKey(
        CompanyBranchLocation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )
    home_edit_requested = models.BooleanField(default=False)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


# Experience Certificate


class ExperienceCertificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resignation = models.ForeignKey(ResignationForm, on_delete=models.CASCADE)
    certificate_file = models.FileField(upload_to='experience_certificates/')
    issued_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Experience Certificate"
    

class CertificateDownloadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    certificate = models.ForeignKey(ExperienceCertificate, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True, default="12.0.0.1")    
