from django.db import models
from django.db import models
from Account.models import *
from Payroll.models import PayrollStatusMaster, designation_master

class Document(models.Model):
    title = models.CharField(max_length=255)
    pdf_file = models.FileField(upload_to='documents/')
    extracted_text = models.TextField(blank=True, null=True)
    keywords = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class application_search(models.Model):
    id = models.AutoField(primary_key=True)
    name =models.TextField(null=True,blank=True)
    description =models.TextField(null=True,blank=True)
    href =models.TextField(null=True,blank=True)
    menu_id =models.TextField(null=True,blank=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='app_search_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='app_search_updated',blank=True, null=True,db_column='updated_by')
    
    class Meta:
        db_table = 'application_search'
    def __str__(self):
        return self.name
         
class parameter_master(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name =models.TextField(null=True,blank=True)
    parameter_value =models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='parameter_created_by',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='parameter_updated_by',blank=True, null=True,db_column='updated_by')
    
    class Meta:
        db_table = 'parameter_master'
    def __str__(self):
        return self.parameter_name


class status_master(models.Model):
    status_id = models.AutoField(primary_key=True)
    status_name = models.TextField(null=True, blank=True)
    status_type = models.TextField(null=True, blank=True)
    status_color = models.TextField(null=True, blank=True)
    is_active = models.IntegerField(default=1)  
    level = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'status_master'

class status_color(models.Model):
    id = models.AutoField(primary_key=True)
    color = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'status_color'

class document_master(models.Model):
    doc_id = models.AutoField(primary_key=True)
    doc_name = models.TextField(null=True, blank=True)
    doc_subpath =models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    updated_by = models.TextField(null=True, blank=True)
    is_active = models.IntegerField(default=1)
    mandatory = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'document_master'


class department_master(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'department_master'

class branch_master(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'branch_master'

class stakeholders(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'stakeholders'

class send_user(models.Model):
    id = models.AutoField(primary_key=True)
    name =  models.TextField(null=True, blank=True)
    email =  models.TextField(null=True, blank=True)
    mobile =  models.TextField(null=True, blank=True)
    department =  models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'send_user'       

class Log(models.Model):
    log_text = models.TextField(null=True,blank=True)
    
    class Meta:
        db_table = 'logs'

class StateMaster(models.Model):
    state_id = models.AutoField(primary_key=True)
    state_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)

    def __str__(self):
        return self.state_name
    
    class Meta:
        db_table = 'state_master'

class CityMaster(models.Model):
    city_id = models.AutoField(primary_key=True)
    city_name = models.CharField(max_length=100)
    state = models.ForeignKey(StateMaster, null=True, blank=True,on_delete=models.CASCADE, related_name='cities')
    district = models.ForeignKey('Masters.DistrictMaster',null=True, blank=True, on_delete=models.CASCADE, related_name='districts_id')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)

    def __str__(self):
        return self.city_name
    
    class Meta:
        db_table = 'city_master'

class DistrictMaster(models.Model):
    district_id = models.AutoField(primary_key=True)
    district_name = models.CharField(max_length=100)
    state = models.ForeignKey(StateMaster,null=True, blank=True, on_delete=models.CASCADE, related_name='districts')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)

    def __str__(self):
        return self.district_name
    
    class Meta:
        db_table = 'district_master'

class sc_employee_master(models.Model):
    id = models.AutoField(primary_key=True)
    employee_id =models.TextField(null=True,blank=True)
    employee_name =models.TextField(null=True,blank=True)
    gender = models.TextField(null=True,blank=True)
    handicapped = models.BooleanField(null=True,blank=True,default=True)
    state_id = models.ForeignKey(StateMaster, on_delete=models.CASCADE,related_name='employee_relation_state_id',blank=True, null=True,db_column='state_id')
    city = models.TextField(null=True,blank=True)
    address = models.TextField(null=True,blank=True)
    pincode  = models.TextField(null=True,blank=True)
    mobile_no =models.TextField(null=True,blank=True)
    email = models.TextField(null=True,blank=True)
    uan_no = models.TextField(null=True,blank=True)
    pf_no = models.TextField(null=True,blank=True)
    esic =  models.TextField(null=True,blank=True)
    bank_name = models.TextField(null=True,blank=True)
    branch_name = models.TextField(null=True,blank=True)
    ifsc_code =  models.TextField(null=True,blank=True)
    account_no =  models.TextField(null=True,blank=True)
    account_holder_name =  models.TextField(null=True,blank=True)
    company_id = models.ForeignKey('Masters.company_master', on_delete=models.CASCADE,related_name='employee_relation',blank=True, null=True,db_column='company_id')
    employment_status = models.ForeignKey(parameter_master, on_delete=models.CASCADE,related_name='parameter_data',blank=True, null=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='sc_employee_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='sc_employee_updated',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'sc_employee_master'
    # def __str__(self):
    #     return self.employee_name


class site_master(models.Model):
    site_id = models.AutoField(primary_key=True)
    company = models.ForeignKey('Masters.company_master', on_delete=models.CASCADE,related_name='company_relation',blank=True, null=True)
    state_id = models.ForeignKey(StateMaster, on_delete=models.CASCADE,related_name='state_master_site_master',blank=True, null=True,db_column="state_id")
    city_id = models.ForeignKey(CityMaster, on_delete=models.CASCADE,related_name='city_master_city_id',blank=True, null=True,db_column="city_id")
    site_name =models.TextField(null=True,blank=True)
    site_address =models.TextField(null=True,blank=True)
    pincode =models.TextField(null=True,blank=True)
    contact_person_name =models.TextField(null=True,blank=True)
    contact_person_email =models.TextField(null=True,blank=True)
    contact_person_mobile_no =models.TextField(null=True,blank=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='site_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='site_updated',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'site_master'
    def __str__(self):
        company_name = self.company.company_name if self.company else "No Company"
        return f"{company_name} - {self.site_name}" if self.site_name else company_name
    

class company_master(models.Model):
    company_id = models.AutoField(primary_key=True)
    company_name = models.TextField(null=True,blank=True)
    company_address =models.TextField(null=True,blank=True)
    pincode =models.TextField(null=True,blank=True)
    contact_person_name =models.TextField(null=True,blank=True)
    contact_person_email =models.TextField(null=True,blank=True)
    contact_person_mobile_no =models.TextField(null=True,blank=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='company_created_by',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='company_updated_by',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'company_master'
    def __str__(self):
        return self.company_name
    
class SlotDetails(models.Model):
    slot_id = models.AutoField(primary_key=True)
    company = models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='slot_relation',blank=True, null=True)
    # worksite = models.TextField(null=True,blank=True)
    setting_id  = models.ForeignKey('Masters.SettingMaster', on_delete=models.CASCADE,related_name='SlotDetails_setting_id',blank=True, null=True,db_column="setting_id")
    site_id = models.ForeignKey(site_master, on_delete=models.CASCADE,related_name='SlotDetails_site_id',blank=True, null=True,db_column="site_id")
    designation_id = models.ForeignKey('Payroll.designation_master', on_delete=models.CASCADE,related_name='SlotDetails_designation_id',blank=True, null=True,db_column="designation_id")
    slot_name = models.TextField(null=True,blank=True)
    slot_description = models.CharField(max_length=200, null=True, blank=True)
    shift_date = models.DateField(null=True,blank=True)
    start_time = models.TextField(null=True,blank=True)
    end_time = models.TextField(null=True,blank=True)
    night_shift = models.BooleanField(null=True,blank=True,default=True)
    status = models.ForeignKey('Payroll.PayrollStatusMaster', on_delete=models.CASCADE,related_name='slot_status',blank=True, null=True,db_column='status_id')
    is_active =models.BooleanField(null=True,blank=True,default=True)
    message = models.TextField(max_length=255,null=True,blank=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='slot_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='slot_updated',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'slot_details'
    def __str__(self):
        return self.slot_name



class SettingMaster(models.Model):
    id= models.AutoField(primary_key=True)
    slot_id = models.ForeignKey(SlotDetails, on_delete=models.CASCADE,related_name='setting_relation',blank=True, null=True,db_column='slot_id')
    noti_start_time =  models.DateField(null=True,blank=True)
    noti_end_time = models.DateField(null=True,blank=True)
    no_of_notification = models.IntegerField(null=True, blank=False)
    no_of_employee =  models.IntegerField(null=True, blank=False)
    interval = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='setting_created',blank=True, null=True,db_column='created_by')
    updated_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='setting_updated',blank=True, null=True,db_column='updated_by')
    class Meta:
        db_table = 'setting_master'
    def __str__(self):
        return self.name
    
class UserSlotDetails(models.Model):
    id = models.AutoField(primary_key=True) 
    emp_id =  models.ForeignKey(sc_employee_master, on_delete=models.CASCADE,related_name='UserSlotDetails_emp_id',blank=True, null=True,db_column='emp_id')
    employee_id = models.TextField(null=True,blank=True)
    company_id = models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='UserSlotDetails_company_id',blank=True, null=True,db_column='company_id')
    site_id = models.ForeignKey(site_master, on_delete=models.CASCADE,related_name='UserSlotDetails_site_id',blank=True, null=True,db_column='site_id')
    slot_id = models.ForeignKey(SlotDetails, on_delete=models.CASCADE,related_name='UserSlotDetails_slot_id',blank=True, null=True,db_column='slot_id')
    status = models.ForeignKey('Payroll.PayrollStatusMaster', on_delete=models.CASCADE,related_name='UserSlotDetails_status_id',blank=True, null=True,db_column='status_id')
    created_at = models.DateTimeField(null=True,blank=True,auto_now_add=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name='user_shit_created',blank=True, null=True,db_column='created_by') 
    class Meta:
        db_table = 'user_slot_details'
    
class employee_designation(models.Model):
    id =  models.AutoField(primary_key=True)
    designation_id = models.ForeignKey(designation_master, on_delete=models.CASCADE,related_name='employee_designation_relation',blank=True, null=True,db_column='designation_id')
    company_id= models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='comapny_designation_relation',blank=True, null=True,db_column='company_id')
    employee_id = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    updated_by = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'employee_designation'
    def __str__(self):
        return self.name
    

class employee_site(models.Model):
    id =  models.AutoField(primary_key=True)
    site_id = models.ForeignKey(site_master, on_delete=models.CASCADE,related_name='employee_site_relation',blank=True, null=True,db_column='site_id')
    company_id= models.ForeignKey(company_master, on_delete=models.CASCADE,related_name='comapny_site_relation',blank=True, null=True,db_column='company_id')
    employee_id =models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    created_by = models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True, auto_now=True)
    updated_by = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'employee_site'
    def __str__(self):
        return self.name
    


