from django.db import models

from Masters.models import company_master, site_master

# Create your models here.
# class AttendanceLog(models.Model):
#     log_id = models.AutoField(primary_key=True, unique=True)
#     employee_id = models.BigIntegerField(null=True, blank=True)
#     year = models.IntegerField(null=True, blank=True)
#     month = models.IntegerField(null=True, blank=True)
#     day = models.IntegerField(null=True, blank=True)
#     status = models.CharField(max_length=255,null=True, blank=True)
#     status_change_time = models.DateTimeField(default=None, null=True, blank=True)
#     latitude = models.CharField(max_length=255,null=True, blank=True)
#     longitude = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'attendance_log'
class DailyAttendance(models.Model):
    employee_id = models.BigIntegerField(null=True, blank=True)
    atten_date = models.DateField(null=True)
    p = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
    a = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
    pl = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
    sl = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
    cl = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
    other_leave = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
    in_time = models.DateTimeField(null=True, blank=True)
    out_time = models.DateTimeField(null=True, blank=True)
    latitude = models.CharField(max_length=255,null=True, blank=True)
    longitude = models.CharField(max_length=255,null=True, blank=True)
    overtime_hours = models.IntegerField(null=True, blank=True)
    is_overtime = models.IntegerField(null=True, blank=True,default="0")
    created_at = models.DateTimeField(default=None, null=True, blank=True)
    created_by = models.CharField(max_length=255,null=True, blank=True)
    updated_at = models.DateTimeField(default=None, null=True, blank=True)
    updated_by = models.CharField(max_length=255,null=True, blank=True)

    class Meta:
        db_table = 'daily_attendance'

# class AttendanceDetails(models.Model):
#     attendance_id = models.AutoField(primary_key=True, unique=True)
#     employee_id = models.BigIntegerField(null=True, blank=True)
#     year = models.IntegerField(null=True, blank=True)
#     month = models.IntegerField(null=True, blank=True)
#     p = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
#     a = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
#     pl = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
#     sl = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
#     cl = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
#     other_leave = models.DecimalField(max_digits = 10,decimal_places =2,null=True, blank=True)
#     overtime_hours = models.TimeField(null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True)
    
    
#     class Meta:
#         db_table = 'attendance_details'
# class LeaveApply(models.Model):
#     leave_id = models.AutoField(primary_key=True, unique=True)
#     employee_id = models.BigIntegerField(null=True, blank=True)
#     from_date =  models.DateField(default=None, null=True, blank=True)
#     to_date =  models.DateField(default=None, null=True, blank=True)
#     leave_id = models.CharField(max_length=255,null=True, blank=True)
#     reason_for_leave  = models.CharField(max_length=255,null=True, blank=True)
#     title  = models.CharField(max_length=255,null=True, blank=True)
#     leave_status_id  = models.CharField(max_length=255,null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True) 
#     class Meta:
#         db_table = 'leave_application_details'
# class EarlyLeaveApply(models.Model):
#     early_leave_id = models.AutoField(primary_key=True, unique=True)
#     employee_id = models.BigIntegerField(null=True, blank=True)
#     leave_date =  models.DateField(default=None, null=True, blank=True)
#     leave_time =  models.TimeField(default=None, null=True, blank=True)
#     reason_for_leave  = models.CharField(max_length=255,null=True, blank=True)
#     title  = models.CharField(max_length=255,null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'early_leave_application'        
# class StatusMaster(models.Model):
#     status_id = models.AutoField(primary_key=True, unique=True)
#     status_name =  models.CharField(max_length=255,null=True, blank=True)
#     status_type =  models.CharField(max_length=255,null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'status_master'
# class CompanyMaster(models.Model):
#     company_id = models.AutoField(primary_key=True, unique=True)
#     company_name =  models.CharField(max_length=255,null=True, blank=True)
#     company_address =  models.CharField(max_length=255,null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'company_master'
# class LocationMaster(models.Model):
#     location_id = models.AutoField(primary_key=True, unique=True)
#     location_name =  models.CharField(max_length=255,null=True, blank=True)
#     company_id =  models.IntegerField(null=True, blank=True)
#     latitude = models.CharField(max_length=255,null=True, blank=True)
#     longitude = models.CharField(max_length=255,null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'location_master'
# class ShiftMaster(models.Model):
#     shift_id = models.AutoField(primary_key=True, unique=True)
#     shift_name = models.CharField(max_length=255,null=True, blank=True)
#     in_shift_time = models.TimeField(max_length=255,null=True, blank=True)
#     out_shift_time = models.TimeField(max_length=255,null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'shift_master'
        
# class UserRelationMaster(models.Model):
#     user_relation_id = models.AutoField(primary_key=True, unique=True)
#     user_id = models.BigIntegerField(max_length=255,null=True, blank=True)
#     company_id = models.BigIntegerField(null=True, blank=True)
#     location_id = models.BigIntegerField(null=True, blank=True)
#     shift_id = models.BigIntegerField(null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'user_relation_master'         

# class TimeCorrection(models.Model):
#     correction_id = models.AutoField(primary_key=True, unique=True)
#     user_id = models.BigIntegerField(max_length=255,null=True, blank=True)
#     title = models.CharField(max_length=255,null=True, blank=True)
#     correction_date = models.DateField(null=True, blank=True)
#     corrected_time = models.TimeField(null=True, blank=True)
#     reason_for_correction = models.CharField(max_length=255,null=True, blank=True)
#     correction_type = models.CharField(max_length=255,null=True, blank=True)
#     status_id = models.IntegerField(null=True, blank=True)
#     created_at = models.DateTimeField(default=None, null=True, blank=True)
#     created_by = models.CharField(max_length=255,null=True, blank=True)
#     updated_at = models.DateTimeField(default=None, null=True, blank=True)
#     updated_by = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'time_correction'         

# class Alerts(models.Model):
#     id = models.AutoField(primary_key=True, unique=True)
#     employee_id = models.BigIntegerField(null=True, blank=True)
#     alert_text = models.CharField(max_length=255,null=True, blank=True)
#     class Meta:
#         db_table = 'alerts'         

    
class ShiftMaster(models.Model):
    shift_id = models.AutoField(primary_key=True)
    shift_name = models.TextField(null=True)
    company_id= models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='comapny_id_q1',null=True,db_column='company_id')    
    site_id = models.ForeignKey(site_master, on_delete=models.CASCADE,related_name='site_id_q1',null=True,db_column='site_id')
    in_time = models.TimeField(null=True)
    out_time = models.TimeField(null=True)
    in_time_buffer = models.TimeField(null=True)
    out_time_buffer = models.TimeField(null=True)
    half_day_in_time = models.TimeField(null=True)
    half_day_out_time = models.TimeField(null=True)
    overtime = models.TimeField(null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)

    class Meta:
        db_table = 'shift_master'
        
class EmployeeShiftMapping(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.TextField(null=True, blank=True)
    employee_id = models.IntegerField(null=True)
    company_id = models.BigIntegerField(null=True, blank=True)
    location_id = models.BigIntegerField(null=True, blank=True)
    shift_id = models.BigIntegerField(null=True, blank=True)
    type_of_attendance = models.TextField(null=True)
    created_at = models.DateTimeField(null=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)

    class Meta:
        db_table = 'employee_shift_mapping'
        
class AttendanceLog(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id = models.IntegerField(null=True)
    company_id= models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='comapny_id_q2',null=True,db_column='company_id')    
    latitude = models.CharField(max_length=255, null=True)
    longitude = models.CharField(max_length=255, null=True)
    atten_date = models.DateField(null=True)
    in_time = models.TimeField(null=True)
    out_time = models.TimeField(null=True)
    created_at = models.DateTimeField(null=True)
    status = models.CharField(max_length=255,null=True, blank=True)
    status_change_time = models.DateTimeField(default=None, null=True, blank=True)
    created_by = models.IntegerField(null=True)
    updated_at = models.DateTimeField(null=True)
    updated_by = models.IntegerField(null=True)

    class Meta:
        db_table = 'attendance_log'      

