from rest_framework import serializers

from Masters.models import *
from Payroll.models import PaySlip, PayoutDetails, daily_salary, salary_generated_log
# class CompanyMasterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = company_master
#         fields = '__all__'  # Include all fields, or specify specific fields as needed

# class SettingMasterListSerializer(serializers.ModelSerializer):
#     class Meta:
#         model=SettingMaster
#         fields = '__all__'

# class ParameterMasterSerializer(serializers.ModelSerializer):  # Corrected serializer class name
#     class Meta:
#         model = parameter_master  # Assuming the model name is in PascalCase, adjust if necessary
#         fields = '__all__'  # This will include all fields in the serialization


# class ScRosterSerializer(serializers.ModelSerializer):
#     company = CompanyMasterSerializer()  # Use the nested serializer

#     class Meta:
#         model = sc_roster
#         fields = '__all__'

# class StateMasterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StateMaster
#         fields = '__all__'

# class SiteSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = site_master
#         fields = '__all__'

# class DesignationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = designation_master
#         fields = '__all__'

# class EmployeeSerializer(serializers.ModelSerializer):
#     company_id = CompanyMasterSerializer()
#     state_id = StateMasterSerializer()
#     employment_status = ParameterMasterSerializer()
#     class Meta:
#         model = sc_employee_master
#         fields = '__all__'

# class EmployeelistSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = sc_employee_master
#         fields = '__all__'

# class SlotDetailsSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SlotDetails
#         fields = '__all__'

# class SlotListDetailsSerializer(serializers.ModelSerializer):
#     company = CompanyMasterSerializer()
#     site_id = SiteSerializer()
#     setting_id = SettingMasterListSerializer()
#     class Meta:
#         model = SlotDetails
#         fields = '__all__'

# class UserSlotDetailsSerializer(serializers.ModelSerializer):
#     slot_id = SlotDetailsSerializer()
#     company_id = CompanyMasterSerializer()
#     site_id = SiteSerializer()
#     # emp_id = EmployeelistSerializer()
#     class Meta:
#         model = UserSlotDetails
#         fields = '__all__'


class DailySalarySerializer(serializers.ModelSerializer):
    # slot_id = SlotDetailsSerializer()

    class Meta:
        model = daily_salary
        fields = ["employee_id", "slot_id", "element_name", "pay_type", "created_at", "amount"]


class PayoutSerialzer(serializers.ModelSerializer):
    # slot_id_d =  SlotDetailsSerializer()

    class Meta:
        model = PayoutDetails


class PaySlipSerializer(serializers.ModelSerializer):
    # slot_id = SlotDetailsSerializer()

    class Meta:
        model = PaySlip
        fields = '__all__'


class SalaryGeneratedSerializer(serializers.ModelSerializer):
    # slot_id = SlotDetailsSerializer()

    class Meta:
        model = salary_generated_log
        fields = '__all__'

# class UserNotificationLogSerializer(serializers.ModelSerializer):
#     slot_id = SlotDetailsSerializer()
#     type = ParameterMasterSerializer()
#     class Meta:
#         model = user_notification_log
#         fields = '__all__'