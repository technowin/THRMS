from django.db import models

class ControlParameterMaster(models.Model):
    id = models.AutoField(primary_key=True)
    control_name = models.TextField(null=True, blank=True)
    control_value = models.TextField(null=True, blank=True)
    is_action = models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)


    class Meta:
        db_table = 'control_parameter_master'

class FormMaster(models.Model):
    form_id = models.AutoField(primary_key=True)
    form_name = models.TextField(null=True, blank=True)
    form_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_master'

    
class Form(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    module = models.IntegerField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form'

class FormField(models.Model):
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=255)
    field_type =  models.CharField(max_length=255,null=True, blank=True)
    section = models.TextField(max_length=255,null=True, blank=True)
    values = models.TextField(null=True,blank=True)
    attributes = models.TextField(null=True,blank=True)
    order = models.IntegerField(default=0)
    is_primary = models.BooleanField(null=True,blank=True)
    foriegn_key_form_id = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)  
    class Meta:
        db_table = 'form_field'

class FieldValidation(models.Model):
    field = models.ForeignKey('Form.FormField',null=True, blank=True, on_delete=models.CASCADE, related_name='validations')
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_validations')
    sub_master =  models.ForeignKey('Form.ValidationMaster',null=True, blank=True,on_delete=models.CASCADE, related_name='field_validations')
    value = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'field_validation'

class FieldDependency(models.Model):
    field = models.ForeignKey(FormField,null=True, blank=True, on_delete=models.CASCADE, related_name='dependencies')
    dependent_on = models.ForeignKey(FormField,null=True, blank=True,on_delete=models.CASCADE, related_name='dependent_fields')
    condition = models.CharField(max_length=255)  
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'field_dependency'

class CommonMaster(models.Model):
    id = models.AutoField(primary_key=True)
    control_value = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    sub_master1 = models.IntegerField(null=True, blank=True)
    sub_master2 = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'common_master'

class FormIncrementNo(models.Model):
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_increment_id')
    form_data = models.TextField(null=True, blank=True)
    increment = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_increment_no'



class ValidationMaster(models.Model):
    field_type = models.TextField(null=True, blank=True)
    control_name = models.TextField(null=True, blank=True)
    control_value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'validation_master'

class RegexPattern(models.Model):
    input_type = models.CharField(max_length=50)
    regex_pattern = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'regex_pattern'

class FormAction(models.Model):
    name = models.TextField(null=True, blank=True)
    is_master =models.BooleanField(null=True,blank=True,default=True)
    is_active =models.BooleanField(null=True,blank=True,default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'form_action'

class FormActionField(models.Model):
    type = models.TextField(null=True, blank=True)
    label_name = models.TextField(null=True, blank=True)
    button_name = models.TextField(null=True, blank=True)
    bg_color = models.TextField(null=True, blank=True)
    text_color = models.TextField(null=True, blank=True)
    button_type = models.TextField(null=True, blank=True)
    dropdown_values = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    action = models.ForeignKey(FormAction,null=True, blank=True, on_delete=models.CASCADE, related_name='form_action')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_action_field'

class FormFieldValues(models.Model):
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_data')
    form_data = models.ForeignKey('Form.FormData',null=True, blank=True, on_delete=models.CASCADE, related_name='form_value_id')
    field = models.ForeignKey('Form.FormField',null=True, blank=True,on_delete=models.CASCADE, related_name='field_value_id')
    value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_field_values'

class FormFile(models.Model):
    file_name = models.TextField(null=True, blank=True)
    uploaded_name = models.TextField(null=True, blank=True)
    file_path = models.TextField(null=True, blank=True)
    file = models.ForeignKey('Form.FormFieldValues',null=True, blank=True, on_delete=models.CASCADE, related_name='file_id')
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_filr_id')
    field = models.ForeignKey('Form.FormField',null=True, blank=True,  on_delete=models.CASCADE, related_name='field_file_id')
    form_data = models.ForeignKey('Form.FormData',null=True, blank=True, on_delete=models.CASCADE, related_name='form_data_id')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_file'

class FormData(models.Model):
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_data_id')
    action = models.ForeignKey('Form.FormAction',null=True, blank=True,on_delete=models.CASCADE, related_name='form_action_id')
    req_no = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_data'

class AttributeMaster(models.Model):
    control_name = models.TextField(null=True, blank=True)
    control_value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'attribute_master'

class ActionData(models.Model):
    value = models.TextField(null=True, blank=True)
    form_data = models.ForeignKey('Form.FormData',null=True, blank=True, on_delete=models.CASCADE, related_name='action_data_id')
    field = models.ForeignKey('Form.FormActionField',null=True, blank=True, on_delete=models.CASCADE, related_name='action_field_id')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'action_data'

class MasterDropdownData(models.Model):
    name = models.TextField(null=True, blank=True)
    query = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'master_drodpown_data'


class FormGenerativeField(models.Model):
    prefix = models.TextField(null=True, blank=True)
    selected_field_id = models.TextField(null=True, blank=True)
    no_of_zero = models.TextField(null=True, blank=True)
    increment = models.TextField(null=True, blank=True)
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_genrative_id')
    field = models.ForeignKey('Form.FormField',null=True, blank=True, on_delete=models.CASCADE, related_name='field_genrative_id')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_generative_field'

class SectionMaster(models.Model):
    name = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'section_master'

class candidate_data(models.Model):
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='candidate_data_id')
    action = models.ForeignKey('Form.FormAction',null=True, blank=True,on_delete=models.CASCADE, related_name='candidate_action_id')
    req_no = models.TextField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'candidate_data'


class candidate_details(models.Model):
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='form_cand_data')
    form_data = models.ForeignKey('Form.candidate_data',null=True, blank=True, on_delete=models.CASCADE, related_name='form_cand_value_id')
    field = models.ForeignKey('Form.FormField',null=True, blank=True,on_delete=models.CASCADE, related_name='field_cand_value_id')
    primary_key = models.TextField(null=True, blank=True)
    value = models.TextField(null=True, blank=True)
    candidate_id = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'candidate_details'


class candidate_file(models.Model):
    file_name = models.TextField(null=True, blank=True)
    uploaded_name = models.TextField(null=True, blank=True)
    file_path = models.TextField(null=True, blank=True)
    file = models.ForeignKey('Form.candidate_details',null=True, blank=True, on_delete=models.CASCADE, related_name='cand_id')
    form = models.ForeignKey('Form.Form',null=True, blank=True, on_delete=models.CASCADE, related_name='cand_filr_id')
    field = models.ForeignKey('Form.FormField',null=True, blank=True,  on_delete=models.CASCADE, related_name='cand_file_id')
    form_data = models.ForeignKey('Form.candidate_data',null=True, blank=True, on_delete=models.CASCADE, related_name='cand_data_id')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'candidate_file'

class FormFieldValuesChaya(models.Model):
    form_id =models.TextField(blank=True, null=True)
    form_data_id = models.TextField(blank=True, null=True)
    field_id = models.TextField(blank=True, null=True)
    value = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_field_values_chaya'


class FormChaya(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_chaya'

class FormFieldChaya(models.Model):
    form_id = models.TextField(blank=True, null=True)
    label = models.CharField(max_length=255)
    field_type =  models.CharField(max_length=255,null=True, blank=True)
    section = models.TextField(max_length=255,null=True, blank=True)
    values = models.TextField(null=True,blank=True)
    attributes = models.TextField(null=True,blank=True)
    order = models.IntegerField(default=0)
    is_primary = models.BooleanField(null=True,blank=True)
    foriegn_key_form_id = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)  
    class Meta:
        db_table = 'form_field_chaya'


class FormFileChaya(models.Model):
    file_name = models.TextField(null=True, blank=True)
    uploaded_name = models.TextField(null=True, blank=True)
    file_path = models.TextField(null=True, blank=True)
    file_id = models.TextField(blank=True, null=True)
    form_id = models.TextField(blank=True, null=True)
    field_id = models.TextField(blank=True, null=True)
    form_data_id = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'form_file_chaya'

class ModuleMaster(models.Model):
    name = models.TextField(null=True, blank=True)
    index_table = models.TextField(null=True,blank=True)
    file_table =models.TextField(null=True,blank=True)
    data_table = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by =  models.TextField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_by =  models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'module_master'







