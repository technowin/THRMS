from rest_framework import serializers
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
    
    
    
    