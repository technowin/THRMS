from rest_framework import serializers

from Account.models import CustomUser
from Workflow.templatetags.custom_filters import CustomTimeField
from .models import *


class AttendanceSerializer(serializers.Serializer):
    
    employee_id = serializers.IntegerField()
    year = serializers.IntegerField()
    month = serializers.IntegerField()
    day = serializers.IntegerField()
    status = serializers.CharField()
    status_change_time = serializers.DateTimeField()
    latitude = serializers.CharField()
    longitude = serializers.CharField()

class LeaveApplySerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    from_date = serializers.DateField()
    to_date = serializers.DateField()
    leave_id = serializers.CharField()
    reason_for_leave = serializers.CharField()
    title = serializers.CharField()
    
class ApplyCorrectionSerializer(serializers.Serializer):
    title = serializers.CharField()
    correction_date = serializers.DateField()
    corrected_time = serializers.DateTimeField()
    reason_for_correction = serializers.CharField()
    employee_id = serializers.CharField()
    type = serializers.CharField()
    

    
class LeaveStatusUpdateSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    status = serializers.CharField()
class AlertSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    text = serializers.CharField()
    
class EarlyLeaveApplySerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    leave_date = serializers.DateField()
    leave_time = serializers.TimeField()
    reason_for_leave = serializers.CharField()
    title = serializers.CharField()    
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email','name']

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class RegistrationSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()
    name = serializers.CharField()

# class AttendanceLogSerializer(serializers.Serializer):
#     employee_id = serializers.IntegerField(allow_null=True, required=False)
#     atten_date = serializers.CharField(allow_null=True, required=False)
#     status = serializers.CharField(allow_null=True, required=False)
#     status_change_time = serializers.CharField(allow_null=True, required=False)
#     latitude = serializers.CharField(allow_null=True, required=False, allow_blank=True)
#     longitude = serializers.CharField(allow_null=True, required=False, allow_blank=True)
#     in_time = serializers.CharField(allow_null=True, required=False, allow_blank=True)
#     out_time = serializers.CharField(allow_null=True, required=False, allow_blank=True)
#     created_at = serializers.CharField(allow_null=True, required=False, allow_blank=True)
#     created_by = serializers.CharField(allow_null=True, required=False, allow_blank=True)
#     updated_at = serializers.CharField(allow_null=True, required=False, allow_blank=True)
#     updated_by = serializers.CharField(allow_null=True, required=False, allow_blank=True)

class AttendanceLogSerializer(serializers.ModelSerializer):
    out_time = CustomTimeField(required=False, allow_null=True)
    
    class Meta:
        model = AttendanceLog
        fields = '__all__' 

    
    
    
    