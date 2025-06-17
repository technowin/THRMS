from django.db import connection
from django.shortcuts import render
from collections import defaultdict

import json
import pydoc
import re
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate, login ,logout,get_user_model
from Account.forms import RegistrationForm
from Account.models import *
from Masters.models import *
import Db 
import bcrypt
from django.contrib.auth.decorators import login_required
from THRMS.encryption import *
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph
from Account.utils import decrypt_email, encrypt_email
import requests
import traceback
import pandas as pd
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib import messages
import openpyxl
from openpyxl.styles import Font, Border, Side
import calendar
from datetime import datetime, timedelta
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q, Count

from django.apps import apps

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from Account.models import *
from Masters.models import *
from Form.models import *
from Account.db_utils import callproc
from django.views.decorators.csrf import csrf_exempt
import os
from django.urls import reverse
from THRMS.settings import *
import logging
from django.http import FileResponse, Http404
import mimetypes
from django.template.loader import render_to_string

from Test.models import CandidateTestMaster
from Workflow.models import history_workflow_details, rec_history_workflow_details, rec_workflow_details, workflow_details, workflow_matrix, workflow_action_master


# Create your views here.
def format_label_name(parameter_name):
    """Convert parameter name to a proper label format."""
    return " ".join(re.findall(r'[A-Za-z]+', parameter_name)).title()

def get_dublicate_name(request):
    if request.method == 'POST':
        form_name = request.POST.get('form_name')
        exists = Form.objects.filter(name=form_name).exists()  
        return JsonResponse({'exists': exists})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def form_builder(request):
    try:
        form_id = request.GET.get('form_id')
        common_options = list(AttributeMaster.objects.values("id", "control_name", "control_value"))
        sub_control = list(ValidationMaster.objects.values("id", "control_name", "control_value", "field_type"))
        regex = list(RegexPattern.objects.values("id", "input_type", "regex_pattern", "description"))
        dropdown_options = list(ControlParameterMaster.objects.values("control_name", "control_value"))
        master_dropdown = list(MasterDropdownData.objects.values("id", "name", "query"))
        form_names = list(Form.objects.values("id","name"))
        section = list(SectionMaster.objects.values("id","name"))
        modules = ModuleMaster.objects.all()
        # version_fields = [field.name for field in WorkflowVersionControl._meta.fields if field.name == 'file_name']
        # version = [name.replace('_', ' ').title() for name in version_fields]


        if not form_id:
            return render(request, "Form/form_builder.html", {
                "modules":modules,
                "regex": json.dumps(regex),
                "dropdown_options": json.dumps(dropdown_options),
                "common_options": json.dumps(common_options),
                "sub_control": json.dumps(sub_control),
                "master_dropdown": json.dumps(master_dropdown),
                "form_names":json.dumps(form_names),
                "section_names":json.dumps(section),
            })

        try:
            form_id = dec(form_id)  # Decrypt form_id
            form = get_object_or_404(Form, id=form_id)
            fields = FormField.objects.filter(form_id=form_id).order_by('order')
            validations = FieldValidation.objects.filter(form_id=form_id)
            generative = FormGenerativeField.objects.filter(form_id=form_id)
        except Exception as e:
            print(f"Error fetching form data: {e}")

        validation_dict = {}
        try:
            for validation in validations:
                field_id = validation.field.id

                if field_id not in validation_dict:
                    validation_dict[field_id] = []

                validation_entry = {
                    "validation_type": validation.sub_master.control_value,
                    "validation_value": validation.value
                }
                validation_dict[field_id].append(validation_entry)

        except Exception as e:
            print(f"Error processing validations: {e}")
            traceback.print_exc()

        generative_list = {}
        for generate in generative:
            field_id = generate.field.id

            if field_id not in generative_list:
                generative_list[field_id] = []

            generative_list[field_id].append({
                "prefix": generate.prefix,
                "selected_field": generate.selected_field_id,
                "no_of_zero": generate.no_of_zero,
                "increment": generate.increment,
            })


        form_fields_json = json.dumps([
            {
                "id": field.id,
                "label": field.label,
                "type": field.field_type,
                "primarykey": 1 if field.is_primary == 1 else 0,
                "foreignkey":field.foriegn_key_form_id,
                "section":field.section,
                "options": field.values.split(",") if field.values else [], 
                "attributes": field.attributes if field.attributes else [],
                "validation": validation_dict.get(field.id, []),
                "generative_list": generative_list
            }
            for field in fields
        ])
    except Exception as e:
        traceback.print_exc()
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)

    return render(request, "Form/form_builder.html", {
        "form": form,
        "modules":modules,
        "regex": json.dumps(regex),
        "form_fields_json": form_fields_json,
        "dropdown_options": json.dumps(dropdown_options),
        "common_options": json.dumps(common_options),
        "sub_control": json.dumps(sub_control),
        "master_dropdown": json.dumps(master_dropdown),
        "form_names":json.dumps(form_names),
        "section_names":json.dumps(section),
    })


def format_label(label):
    """Format label to have proper capitalization."""
    words = re.split(r'[_ ]+', label.strip())
    return ' '.join(word.capitalize() for word in words)





@csrf_exempt
def save_form(request):
    user  = request.session.get('user_id', '')
    try:
        if request.method == "POST":
            form_name = request.POST.get("form_name")
            form_description = request.POST.get("form_description")
            module = request.POST.get("module")
            form_data_json = request.POST.get("form_data")

            table_name = get_object_or_404(ModuleMaster,id = module).data_table

            if not form_data_json:
                return JsonResponse({"error": "No form data received"}, status=400)

            try:
                form_data = json.loads(form_data_json)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            
            form = Form.objects.create(name=form_name, description=form_description, module=module)
            index = 0
            generative_fields = [] 

            for  index,field in enumerate(form_data):
               
                if field.get("type") == "master dropdown":
                    value = field.get("masterValue")

                elif field.get("type") == "multiple":
                    value = field.get("multiMasterValue")

                elif field.get("type") == "field_dropdown":
                    dropdown_mappings = field.get("field_dropdown", [])
                    form_id_selected = dropdown_mappings.get("form_id","")
                    field_id_selected = dropdown_mappings.get("field_id","")
                    if form_id_selected and field_id_selected:
                        value = f"{form_id_selected},{field_id_selected}"
            
                    # value = dec(value)
                else:
                    value=",".join(option.strip() for option in field.get("options", []))

                
                formatted_label = format_label(field.get("label", ""))
                order = field.get("order","")

                form_field = FormField.objects.create(
                    form=form,
                    label=formatted_label, 
                    section = field.get("section",""), # Use formatted label here
                    field_type=field.get("type", ""),
                    attributes=field.get("attributes", "[]"),
                    is_primary = field.get("primarykey"),
                    foriegn_key_form_id = field.get("foreignkey",""),
                    values=value,
                    created_by=request.session.get('user_id', '').strip(),
                    order=order
                )
                
                field_id = form_field.id

               
                # Handle regex & max_length validation separately
                if "validation" in field and isinstance(field["validation"], list):
                    for validation_item in field["validation"]:
                        validation_type = validation_item.get("validation_type")
                        validation_value = validation_item.get("validation_value", "")
                        sub_master_id = validation_item.get("id")  # Get sub_master_id for regex

                        if validation_type and validation_value and sub_master_id:
                            FieldValidation.objects.create(
                                field=get_object_or_404(FormField, id=field_id),
                                form=get_object_or_404(Form, id=form.id),
                                sub_master_id=sub_master_id,  # Save regex/max_length master ID
                                value=validation_value,
                                created_by = request.session.get('user_id', '').strip()  # Save regex pattern or max_length
                            )


                # ✅ Save `file` validation (New Logic)
                if field.get("type") == "file" and "validation" in field:
                    file_validation_list = field["validation"]  # This is a list

                    if file_validation_list and isinstance(file_validation_list, list):
                        file_validation = file_validation_list[0]  # Get first item (dictionary)

                        file_validation_value = file_validation.get("validation_value", "")  # Extract ".jpg, .jpeg, .png"
                        sub_master_id = file_validation.get("id", None)  # Extract "2"

                        # Create FieldValidation record
                        FieldValidation.objects.create(
                            field=get_object_or_404(FormField, id=field_id),
                            form=get_object_or_404(Form, id=form.id),
                            sub_master_id=sub_master_id,  # Save only the ID
                            value=file_validation_value,
                            created_by = request.session.get('user_id', '').strip()
                        )

                if field.get("type") == "file multiple" and "validation" in field:
                    file_validation_list = field["validation"]  # This is a list of validation dicts

                    if file_validation_list and isinstance(file_validation_list, list):
                        for file_validation in file_validation_list:
                            file_validation_value = file_validation.get("validation_value", "")
                            sub_master_id = file_validation.get("id", None)

                            FieldValidation.objects.create(
                                field=get_object_or_404(FormField, id=field_id),
                                form=get_object_or_404(Form, id=form.id),
                                sub_master_id=sub_master_id,
                                value=file_validation_value,
                                created_by = request.session.get('user_id', '').strip()
                            )

                if field.get("type") == "generative":
                    generative_fields.append({
                        "form_field": form_field,
                        "prefix": field.get("prefix", ""),
                        "field_names": field.get("field_name", []),
                        "no_of_zero": field.get("no_of_zero", ""),
                        "increment": field.get("increment", "")
                    })

                

                    for gen_field in generative_fields:
                        
                        prefix = gen_field["prefix"]
                        if isinstance(prefix, (list, tuple)):
                            prefix = prefix[0] if prefix else ""

                        field_ids = FormField.objects.filter(
                            form=form,
                            label__in=gen_field["field_names"]
                        ).values_list("id", flat=True)

                        FormGenerativeField.objects.create(
                            prefix=gen_field["prefix"],
                            selected_field_id=",".join(map(str, field_ids)),  # Convert IDs to comma-separated string
                            no_of_zero=gen_field["no_of_zero"],
                            increment=gen_field["increment"],
                            form=form,
                            field=gen_field["form_field"]
                        )




            callproc('create_dynamic_form_views',[table_name])
            messages.success(request, "Form and fields saved successfully!!")
            new_url = f'/masters?entity=form&type=i'
            return redirect(new_url) 

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log", [fun, str(e), user])
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)

    finally:
        Db.closeConnection()



@csrf_exempt
def update_form(request, form_id):
    user = request.session.get('user_id', '')
    try:
        if request.method == "POST":
            form_name = request.POST.get("form_name")
            form_description = request.POST.get("form_description")
            module = request.POST.get("module")
            form_data_json = request.POST.get("form_data")

            data_table = get_object_or_404(ModuleMaster,id = module).data_table
            index_table = get_object_or_404(ModuleMaster,id = module).index_table
            file_table = get_object_or_404(ModuleMaster,id = module).file_table

            if not form_data_json:
                return JsonResponse({"error": "No form data received"}, status=400)

            try:
                form_data = json.loads(form_data_json)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)
            
            FieldValidation.objects.filter(form=form_id).delete()

            
            form = get_object_or_404(Form, id=form_id)
            form.name = form_name
            form.description = form_description
            form.module = module
            updated_by = request.session.get('user_id', '').strip()
            form.save()
            index = 0
            # existing_field_ids = set(FormField.objects.filter(form=form).values_list("id", flat=True))
            # incoming_field_ids = set()

            existing_field_ids = set(FormField.objects.filter(form=form).values_list("id", flat=True))
            incoming_field_ids = set()

            for field in form_data:
                if field.get("id"):
                    incoming_field_ids.add(int(field["id"]))

            generative_fields = [] 

            for index,field in enumerate(form_data):
                attributes_value = field.get("attributes", "[]")
                field_id = field.get("id", "")
                formatted_label = format_label(field.get("label", ""))
                order = field.get("order","")

                primary_value = field.get("primarykey")

                if primary_value == 0:
                    primary_value = field.get("primary")

                

                if field.get("type") == "master dropdown" :
                    value = field.get("masterValue")

                elif field.get("type") == "multiple":
                    value = field.get("multiMasterValue")

                
                elif field.get("type") == "field_dropdown":
                    dropdown_mappings = field.get("field_dropdown", [])
                    if dropdown_mappings:
                        form_id_selected = dropdown_mappings.get("form_id","")
                        field_id_selected = dropdown_mappings.get("field_id","")
                        if form_id_selected and field_id_selected:
                            value = f"{form_id_selected},{field_id_selected}"

                    else:
                        if field.get("options"):
                            # Assuming options is an array like ["91", "1206"]
                            value = f"{field['options'][0]},{field['options'][1]}"  # First option as form_id, second as field_id
                        else:
                            value = ""
                    
                    # Store the value
                    field["value"] = value

                else:
                    value = ",".join(option.strip() for option in field.get("options", []))

                if field_id:
                    try:
                        form_field = FormField.objects.get(id=field_id)
                        form_field.label = formatted_label
                        form_field.field_type = field.get("type", "")
                        form_field.section = field.get("section","")
                        form_field.attributes = attributes_value
                        form_field.is_primary = primary_value
                        form_field.foriegn_key_form_id = field.get("foreignkey")
                        form_field.values = value
                        form_field.order = order
                        form_field.updated_by = user
                        form_field.save()
                    except FormField.DoesNotExist:
                        # Field ID not found, create new
                        form_field = FormField.objects.create(
                            form=form,
                            label=formatted_label,
                            field_type=field.get("type", ""),
                            attributes=attributes_value,
                            is_primary = field.get("primarykey"),
                            foriegn_key_form_id = field.get("foreignkey"),
                            values=value,
                            created_by=user,
                            order=order
                        )
                else:
                    # New field with no ID
                    form_field = FormField.objects.create(
                        form=form,
                        label=formatted_label,
                        field_type=field.get("type", ""),
                        attributes=attributes_value,
                        is_primary = field.get("primarykey"),
                        foriegn_key_form_id = field.get("foreignkey"),
                        values=value,
                        created_by=user,
                        order=order
                    )

                field_id = form_field.id



                # ✅ Ensure 'subValues' exists
                if "validation" in field and isinstance(field["validation"], list):
                    for validation_item in field["validation"]:
                        validation_type = validation_item.get("validation_type")
                        validation_value = validation_item.get("validation_value", "")
                        sub_master_id = validation_item.get("id")  # Get sub_master_id for regex

                        if validation_type and validation_value and sub_master_id:
                            FieldValidation.objects.create(
                                field=get_object_or_404(FormField, id=field_id),
                                form=get_object_or_404(Form, id=form.id),
                                sub_master_id=sub_master_id,  # Save regex/max_length master ID
                                value=validation_value, 
                                created_by = user,
                                updated_by = user
                            )
                if field.get("type") == "file" and "validation" in field:
                    file_validation_list = field["validation"]  # This is a list

                    if file_validation_list and isinstance(file_validation_list, list):
                        file_validation = file_validation_list[0]  # Get first item (dictionary)

                        file_validation_value = file_validation.get("validation_value", "")  # Extract ".jpg, .jpeg, .png"
                        sub_master_id = file_validation.get("id", None)  # Extract "2"
                        FieldValidation.objects.filter(field_id=field_id, form_id=form.id).delete()

                        # Then insert new validation
                        FieldValidation.objects.create(
                            field=get_object_or_404(FormField, id=field_id),
                            form=get_object_or_404(Form, id=form.id),
                            sub_master_id=sub_master_id,
                            value=validation_value, 
                            created_by = user,
                            updated_by = user
                        )


                elif field.get("type") == "file multiple" and "validation" in field:
                    file_validation_list = field["validation"]  # This is a list of validation dicts

                    if file_validation_list and isinstance(file_validation_list, list):
                        file_validation = file_validation_list[0]  # Get first item (dictionary)

                        file_validation_value = file_validation.get("validation_value", "")  # Extract ".jpg, .jpeg, .png"
                        sub_master_id = file_validation.get("id", None)  # Extract "2"

                        FieldValidation.objects.filter(field_id=field_id, form_id=form.id).delete()

                        # Then insert new validation
                        FieldValidation.objects.create(
                            field=get_object_or_404(FormField, id=field_id),
                            form=get_object_or_404(Form, id=form.id),
                            sub_master_id=sub_master_id,
                            value=validation_value, 
                            created_by = user,
                            updated_by = user
                        )


                if field.get("type") == "generative":
                    generative_fields.append({
                        "form_field": form_field,
                        "prefix": field.get("prefix", ""),
                        "field_ids": field.get("field_name", []),
                        "no_of_zero": field.get("no_of_zero", ""),
                        "increment": field.get("increment", "")
                    })


                for gen_field in generative_fields:
                    prefix = gen_field["prefix"]
                    if isinstance(prefix, (list, tuple)):
                        prefix = prefix[0] if prefix else ""

                    field_ids = FormField.objects.filter(
                        form=form,
                        label__in=gen_field["field_ids"]
                    ).values_list("id", flat=True)

                    # Skip if all critical fields are empty
                    if not prefix and not field_ids and not gen_field["no_of_zero"] and not gen_field["increment"]:
                        continue
                    else:
                        FormGenerativeField.objects.filter(form_id=form.id).delete()

                        FormGenerativeField.objects.create(
                            prefix=prefix,
                            selected_field_id=",".join(map(str, field_ids)),  # Convert IDs to comma-separated string
                            no_of_zero=gen_field["no_of_zero"],
                            increment=gen_field["increment"],
                            form=form,
                            field=gen_field["form_field"]
                        )

                removed_field_ids = existing_field_ids - incoming_field_ids
                if removed_field_ids:
                    FormField.objects.filter(id__in=removed_field_ids).delete()
           

            callproc('create_dynamic_form_views',[data_table,file_table,index_table])
            messages.success(request, "Form updated successfully!!")
            return redirect('/masters?entity=form&type=i')
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log", [fun, str(e), request.user])
        messages.error(request, "Oops...! Something went wrong!")
        return JsonResponse({"error": "Something went wrong!"}, status=500)
    finally:
        Db.closeConnection()

def form_action_builder(request):
    action_id = request.GET.get('action_id')
    master_values = FormAction.objects.filter(is_master = 1).all()
    button_type = list(CommonMaster.objects.filter(type='button').values("control_value"))
    dropdown_options = list(ControlParameterMaster.objects.filter(is_action=1).values("control_name", "control_value"))

    if not action_id:  
        return render(request,  "Form/form_action_builder.html", {
            "master_values":master_values,
            "button_type":json.dumps(button_type),
            "dropdown_options": json.dumps(dropdown_options),
        })

    try:
        action_id = dec(action_id)  # Decrypt form_id
        form = get_object_or_404(FormAction, id=action_id) 
        fields = FormActionField.objects.filter(action_id=action_id)
    except Exception as e:
        print(f"Error fetching form data: {e}")  # Debugging
        return render(request, "Form/form_action_builder.html", {\
            "dropdown_options": json.dumps(dropdown_options),
            "error": "Invalid form ID"
        })

    form_fields_json = json.dumps([
        {
            "id": field.id,
            "label": field.label_name,
            "bg_color":field.bg_color,
            "text_color":field.text_color,
            "type": field.type,
            "options": field.dropdown_values.split(",") if field.dropdown_values else [],
            "button_type":field.button_type,
            "status":field.status,
            "value":field.button_name
        }
        for field in fields
    ])

    return render(request, "Form/form_action_builder.html", {
        "form": form,
        "master_values":master_values,
        "button_type":json.dumps(button_type),
        "form_fields_json": form_fields_json,
        "dropdown_options": json.dumps(dropdown_options),
    })



@csrf_exempt
def save_form_action(request):
    user  = request.session.get('user_id', '')
    try:

        if request.method == "POST":
            form_name = request.POST.get("action_name")
            form_master = 1 if request.POST.get("is_master") == "on" else 0
            form_data_json = request.POST.get("form_data")

            if not form_data_json:
                return JsonResponse({"error": "No form data received"}, status=400)

            try:
                form_data = json.loads(form_data_json)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            
            form_action = FormAction.objects.create(name=form_name,is_master= form_master,created_by = user)


            for field in form_data:
                field_type = field.get("type", "")
                
                if field_type == "button":
                    label_name = None
                    dropdown_values = None
                    bg_color = field.get("bg_color", "")
                    text_color = field.get("text_color", "")
                    status = field.get("status","")
                    button_name = field.get("value", "")
                else:
                    label_name = field.get("label", "")
                    button_name= None
                    bg_color = None
                    text_color = None
                    status = field.get("status", None)
                    if status in ["", "[]", [], {}, None]:
                        status = None
                    

                # Create the form field entry
                FormActionField.objects.create(
                    action=form_action,
                    type=field_type,
                    label_name=label_name,
                    button_name= button_name,
                    bg_color=bg_color,
                    text_color=text_color,
                    button_type=field.get("button_type", ""),
                    status=status,
                    dropdown_values=",".join(option.strip() for option in field.get("options", [])),
                    created_by = user
                )

            messages.success(request, "Form Action and fields saved successfully!!")
            new_url = f'/masters?entity=action&type=i'
            return redirect(new_url) 

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log", [fun, str(e), user])
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)

    finally:
        Db.closeConnection()

@csrf_exempt
def update_action_form(request, form_id):
    user  = request.session.get('user_id', '')
    try:  # Decoding action_id if necessary

        if request.method == "POST":
            # Getting form data from POST request
            form_name = request.POST.get("action_name")
            form_master = 1 if request.POST.get("is_master") == "on" else 0
            form_data_json = request.POST.get("form_data")

            if not form_data_json:
                return JsonResponse({"error": "No form data received"}, status=400)

            try:
                form_data = json.loads(form_data_json)
            except json.JSONDecodeError:
                return JsonResponse({"error": "Invalid JSON data"}, status=400)

            # Update the FormAction instance
            form_action = FormAction.objects.filter(id=form_id).first() if form_id else None
            if not form_action:
                return JsonResponse({"error": "Form action not found"}, status=404)

            form_action.name = form_name
            form_action.is_master = form_master
            form_action.updated_by= user
            form_action.save()

            # Delete existing form fields for this action
            FormActionField.objects.filter(action_id=form_id).delete()

            # Insert the new form fields
            for field in form_data:
                field_type = field.get("type", "").strip()

                if field_type == "button":
                    label_name = None
                    bg_color = field.get("bg_color", "")
                    text_color = field.get("text_color", "")
                    status = field.get("status", None).strip() if field.get("status") else None
                    button_name = field.get("value", "").strip()
                else:
                    label_name = field.get("label", "").strip()
                    button_name = None
                    bg_color = None
                    text_color = None
                    status = field.get("status", None)
                    if status in ["", "[]", [], {}, None]:
                        status = None
                    

                # Create the form field entry
                FormActionField.objects.create(
                    action=form_action,
                    type=field_type,
                    label_name=label_name,
                    button_name=button_name,
                    bg_color=bg_color,
                    text_color=text_color,
                    button_type=field.get("button_type", ""),
                    status=status,
                    dropdown_values=",".join(option.strip() for option in field.get("options", [])),
                    updated_by = user,
                    created_by = user
                )

            messages.success(request, "Form Action and fields Updated successfully!!")
            new_url = f'/masters?entity=action&type=i'
            return redirect(new_url)

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        # Log error in the database
        callproc("stp_error_log", [fun, str(e), user])
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)

    finally:
        Db.closeConnection()



def form_master(request):
    try:

        if request.method == "POST":
            try:
                form_id = request.POST.get("form")
                form = get_object_or_404(Form, id=form_id)

                raw_fields = FormField.objects.filter(form_id=form_id).values(
                    "id", "label", "field_type", "values", "attributes", "form_id", "form_id__name", "section"
                ).order_by("order")

                sectioned_fields = {}

                for field in raw_fields:
                    # Clean up values and attributes
                    field["values"] = [v.strip() for v in field["values"].split(",")] if field.get("values") else []
                    field["attributes"] = [a.strip() for a in field["attributes"].split(",")] if field.get("attributes") else []

                    # Get section name
                    section_id = field.get("section")
                    if section_id:
                        try:
                            section = SectionMaster.objects.get(id=section_id)
                            section_name = section.name
                        except SectionMaster.DoesNotExist:
                            section_name = ""
                    else:
                        section_name = ""

                    field["section_name"] = section_name

                    # Fetch validations
                    validations = FieldValidation.objects.filter(
                        field_id=field["id"], form_id=form_id
                    ).values("value")
                    field["validations"] = list(validations)

                    # Regex detection
                    if any("^" in v["value"] for v in field["validations"]):
                        field["field_type"] = "regex"
                        pattern_value = field["validations"][0]["value"]
                        try:
                            regex_obj = RegexPattern.objects.get(regex_pattern=pattern_value)
                            field["regex_id"] = regex_obj.id
                            field["regex_description"] = regex_obj.description
                        except RegexPattern.DoesNotExist:
                            field["regex_id"] = None
                            field["regex_description"] = ""



                    # Accept type (file/text)
                    if field["field_type"] in ["file", "file multiple", "text"]:
                        file_validation = next((v for v in field["validations"]), None)
                        field["accept"] = file_validation["value"] if file_validation else ""

                    # Field Dropdown (dynamic values)
                    if field["field_type"] == "field_dropdown":
                        split_values = field["values"]
                        if len(split_values) == 2:
                            dropdown_form_id, dropdown_field_id = split_values
                            field_values = FormFieldValues.objects.filter(field_id=dropdown_field_id).values("value").distinct()
                            field["dropdown_data"] = list(field_values)

                    # Master Dropdown
                    if field["field_type"] == "master dropdown" and field["values"]:
                        dropdown_id = field["values"][0]
                        try:
                            master_data = MasterDropdownData.objects.get(id=dropdown_id)
                            query = master_data.query
                            result = callproc("stp_get_query_data", [query])
                            field["values"] = [{"id": row[0], "name": row[1]} for row in result]
                        except MasterDropdownData.DoesNotExist:
                            field["values"] = []

                    if field["field_type"] == "multiple" and field["values"]:
                        dropdown_id = field["values"][0]
                        try:
                            master_data = MasterDropdownData.objects.get(id=dropdown_id)
                            query = master_data.query
                            result = callproc("stp_get_query_data", [query])
                            field["values"] = [{"id": row[0], "name": row[1]} for row in result]
                        except MasterDropdownData.DoesNotExist:
                            field["values"] = []

                    # Group by section name
                    sectioned_fields.setdefault(section_name, []).append(field)

                context = {
                    "sectioned_fields": sectioned_fields,
                    "type": "master",
                    "form_name": form
                }
                html = render_to_string("Form/_formfields.html", context)
                return JsonResponse({'html': html}, safe=False)
            except Exception as e:
                traceback.print_exc()
                messages.error(request, 'Oops...! Something went wrong!')
                return JsonResponse({"error": "Something went wrong!"}, status=500)
        


        

        
        else:
            form_data_id = request.GET.get("form")
            edit_type = request.GET.get("type")
        
            if form_data_id:
                form_data_id = dec(form_data_id)
                    
                module_id = 1
                module_tables = common_module_master(module_id)

                IndexTable = apps.get_model('Form', module_tables["index_table"])
                DataTable = apps.get_model('Form', module_tables["data_table"])
                FileTable = apps.get_model('Form', module_tables["file_table"])
                form_instance = IndexTable.objects.filter(id=form_data_id).values("id","form_id", "action_id").first()
                
                if form_instance:
                    form_id = form_instance["form_id"]
                    
                    
                    form = get_object_or_404(Form, id=form_id)

                    fields = FormField.objects.filter(form_id=form_id).values(
                        "id", "label", "field_type", "values", "attributes", "form_id", "form_id__name", "section"
                    ).order_by("order")
                    field_values = DataTable.objects.filter(form_data_id=form_data_id).values("field_id", "value")
                    field_values = list(fields)
                    field_values = DataTable.objects.filter(form_data_id=form_data_id).values("field_id", "value")
                    values_dict = {fv["field_id"]: fv["value"] for fv in field_values}

                    sectioned_fields = defaultdict(list)


                    for field in fields:
                        # Split values and attributes
                        field["values"] = field["values"].split(",") if field.get("values") else []
                        field["attributes"] = field["attributes"].split(",") if field.get("attributes") else []

                        # Section name logic
                        section_id = field.get("section")
                        if section_id:
                            try:
                                section = SectionMaster.objects.get(id=section_id)
                                section_name = section.name
                            except SectionMaster.DoesNotExist:
                                section_name = ""
                        else:
                            section_name = ""

                        validations = FieldValidation.objects.filter(
                            field_id=field["id"], form_id=form_id
                        ).values("value")
                        field["validations"] = list(validations)

                        # Regex detection
                        if any("^" in v["value"] for v in field["validations"]):
                            field["field_type"] = "regex"
                            pattern_value = field["validations"][0]["value"]
                            try:
                                regex_obj = RegexPattern.objects.get(regex_pattern=pattern_value)
                                field["regex_id"] = regex_obj.id
                                field["regex_description"] = regex_obj.description
                            except RegexPattern.DoesNotExist:
                                field["regex_id"] = None
                                field["regex_description"] = ""

                        # File field logic
                        if field["field_type"] in ["file", "file multiple","text"]:
                            file_validation = next((v for v in field["validations"]), None)
                            field["accept"] = file_validation["value"] if file_validation else ""

                            file_exists = FileTable.objects.filter(field_id=field["id"], form_data_id=form_data_id).exists()
                            field["file_uploaded"] = 1 if file_exists else 0

                            if file_exists and "required" in field["attributes"]:
                                field["attributes"].remove("required")


                        # Set saved value
                        saved_value = values_dict.get(field["id"], "")
                        if field["field_type"] == "select multiple":
                            field["value"] = [val.strip() for val in saved_value.split(",") if val.strip()]
                        else:
                            field["value"] = saved_value


                        # field_dropdown logic
                        if field["field_type"] == "field_dropdown":
                            split_values = field["values"]
                            if len(split_values) == 2:
                                try:
                                    dropdown_field_id = int(split_values[1])
                                    dropdown_field_values = DataTable.objects.filter(field_id=dropdown_field_id)
                                    field["dropdown_data"] = list(dropdown_field_values.values())
                                    field["saved_value"] = values_dict.get(field["id"])
                                except (ValueError, IndexError):
                                    field["dropdown_data"] = []
                                    field["saved_value"] = ""



                        # master dropdown logic
                        if field["field_type"] == "master dropdown" and field["values"]:
                            try:
                                dropdown_id = field["values"][0]
                                master_data = MasterDropdownData.objects.get(id=dropdown_id)
                                query = master_data.query
                                result = callproc("stp_get_query_data", [query])
                                field["values"] = [{"id": row[0], "name": row[1]} for row in result]
                            except (MasterDropdownData.DoesNotExist, IndexError):
                                field["values"] = []

                        if field["field_type"] == "multiple":
                            try:
                                dropdown_id = field["values"][0]
                                master_data = MasterDropdownData.objects.get(id=dropdown_id)
                                query = master_data.query
                                result = callproc("stp_get_query_data", [query])
                                field["values"] = [{"id": row[0], "name": row[1]} for row in result]
                            except (MasterDropdownData.DoesNotExist, IndexError):
                                field["values"] = []

                        

                        # Group field by section name
                        sectioned_fields[section_name].append(field)

                    # ✅ Fetch action fields (no validations needed)
                    
                    # if edit_type == "edit_type":
                    return render(request, "Form/_formfieldsedit.html", {"sectioned_fields": dict(sectioned_fields),"fields": fields,"type":"edit","form":form,"form_data_id":form_data_id,"edit_type":edit_type})
                    # else:
                    #     return render(request, "Form/_formfieldedit.html", {"sectioned_fields": dict(sectioned_fields),"fields": fields,"type":"edit","form":form,"form_data_id":form_data_id})
            else:
                type = request.GET.get("type")
                form = Form.objects.all()
                return render(request, "Form/form_master.html", {"form": form,"type":type})
    
    except Exception as e:
        traceback.print_exc()
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)
    

def common_module_master(module_id):
    try: # assuming this is the field that links Form to ModuleMaster
        module = get_object_or_404(ModuleMaster, id=module_id)

        return {
            "index_table": module.index_table,  # this should be the model class or its name
            "data_table": module.data_table,
            "file_table": module.file_table,
        }
    except Exception as e:
        raise Exception(f"Error in retrieving module tables: {str(e)}")


def common_form_post(request):
    user = request.session.get('user_id', '')
    role_id = request.session.get('role_id')
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request method"}, status=400)
        
        created_by = user
        form_name = request.POST.get('form_name', '').strip()
        type = request.POST.get('type','')

        workflow_YN = request.POST.get('workflow_YN', '')
        form_id = request.POST.get("form_id")
        editORcreate  = request.POST.get('editORcreate','')
        firstStep = request.POST.get("firstStep")
        # form_id = request.POST.get(form_id_key, '').strip()
        form = get_object_or_404(Form, id=request.POST.get("form_id"))
        module_id = form.module
        module_tables = common_module_master(module_id)
        if role_id == '7':
            status = 1
        else:
            status = 0

        IndexTable = apps.get_model('Form', module_tables["index_table"])
        DataTable = apps.get_model('Form', module_tables["data_table"])
        FileTable = apps.get_model('Form', module_tables["file_table"])

        if form_id == '1':
            special_field_ids = {'539', '540', '552', '544', '778'}
            saved_special_fields = {} 


        if type != 'master':
            # action_id = request.PSOT.get("action_id")action_id = request.POST.get(action_id_key, '').strip()
            action = get_object_or_404(FormAction,id  = request.POST.get("action_id") )

        if type == 'master':
            form_data = IndexTable.objects.create(form=form)
        else:
            form_data = IndexTable.objects.create(form=form,action=action)
        form_data.status = status
        form_data.req_no = f"UNIQ-00{form_data.id}"

        form_data.created_by = user
        form_data.save()

        form_dataID = form_data.id

        # Process each field
        special_field_ids = {'539', '540', '552', '544', '778'}
        saved_special_fields = {}

        for key, value in request.POST.items():
            if key.startswith("field_id_"):
                field_id = value.strip()
                field = get_object_or_404(FormField, id=field_id)
                is_primary = field.is_primary
                primary = 1 if is_primary == 1 else 0

                if field.field_type == "generative":
                    continue

                # Set input_value based on field type
                if field.field_type in ["select multiple", "multiple"]:
                    selected_values = request.POST.getlist(f"field_{field_id}")
                    input_value = ','.join([val.strip() for val in selected_values if val.strip()])
                else:
                    input_value = request.POST.get(f"field_{field_id}", "").strip()

                # ✅ Now safe to use input_value here
                if field_id in special_field_ids:
                    saved_special_fields[field_id] = input_value

                # Save to DataTable
                DataTable.objects.create(
                    form_data=form_data,
                    form=form,
                    field=field,
                    value=input_value,
                    primary_key=primary,
                    created_by=created_by
                )
        

               
        handle_uploaded_files(request, form_name, created_by, form_data, user,module_id)
        final_value = handle_generative_fields(form, form_data, created_by ,module_id)

        CandidateTestMaster.objects.create(
            candidate_id=final_value,
            name=saved_special_fields.get('539'),
            email=saved_special_fields.get('540'),
            mobile=saved_special_fields.get('544'),
            post=saved_special_fields.get('552'),
            form_data_id = form_dataID,
            created_at=timezone.now(),
            created_by = user 
        )

        messages.success(request, "Form data saved successfully!")
        if workflow_YN == '1':
            wfdetailsid = request.POST.get('wfdetailsid', '')
            role_idC = request.POST.get('role_id', '')
            form_id = request.POST.get('form_id', '')
            step_id = request.POST.get('step_id', '')
            if wfdetailsid and wfdetailsid != 'undefined':
                wfdetailsid=dec(wfdetailsid)
            else:
                wfdetailsid = None  
            
            if step_id:
                matrix_entry = rec_workflow_details.objects.filter(id=step_id).first()
                if matrix_entry:
                    status_from_matrix = matrix_entry.status  # adjust field name if needed
                    
            if wfdetailsid and rec_workflow_details.objects.filter(id=wfdetailsid).exists():
                # Update existing record
                workflow_detail = rec_workflow_details.objects.get(id=wfdetailsid)
                workflow_detail.form_data_id = form_dataID
                workflow_detail.role_id = request.POST.get('role_id', '')
                workflow_detail.action_details_id = request.POST.get('action_id', '')
                workflow_detail.step_id = request.POST.get('step_id', '')
                workflow_detail.increment_id += 1
                workflow_detail.status = status_from_matrix or ''
                workflow_detail.updated_at = datetime.now()
                workflow_detail.updated_by = user 
                workflow_detail.save()    
            else:    
                workflow_detail = rec_workflow_details.objects.create(
                form_data_id=form_dataID,
                role_id=request.POST.get('role_id', ''),
                action_details_id=request.POST.get('action_id', ''),
                increment_id=1,
                form_id=request.POST.get('form_id', ''),
                action_id=request.POST.get('action_id', ''),
                status = status_from_matrix or '',
                step_id=request.POST.get('step_id', ''),
                # user_id=user,
                candidate_id = final_value,
                created_at = datetime.now(),
                created_by=user,
                updated_by = user,
                
                )

            # Now set and save req_id using the generated ID
            workflow_detail.req_id = f"REQNO-00{workflow_detail.id}"
            workflow_detail.save()
            if wfdetailsid and rec_workflow_details.objects.filter(id=wfdetailsid).exists():
                rec_history_workflow_details.objects.create(
                    form_data_id=workflow_detail.form_data_id,
                    role_id=workflow_detail.role_id,
                    action_details_id=workflow_detail.action_details_id,
                    increment_id=workflow_detail.increment_id,
                    step_id=workflow_detail.step_id,
                    status=workflow_detail.status,
                    candidate_id = final_value,
                    # user_id=workflow_detail.user_id,
                    # req_id=workflow_detail.req_id,
                    form_id=request.POST.get('form_id', ''),
                    created_by=workflow_detail.updated_by,
                    created_at=workflow_detail.updated_at,
                    history_created_at =datetime.now(),
                    history_created_by = user
                )
            else:
                rec_history_workflow_details.objects.create(
                    form_data_id=workflow_detail.form_data_id,
                    role_id=workflow_detail.role_id,
                    action_details_id=workflow_detail.action_details_id,
                    increment_id=workflow_detail.increment_id,
                    step_id=workflow_detail.step_id,
                    status=workflow_detail.status,
                    # user_id=workflow_detail.user_id,
                    # req_id=workflow_detail.req_id,
                    # operator=request.POST.get('custom_dropdownOpr', ''),
                    candidate_id = final_value,
                    form_id=request.POST.get('form_id', ''),
                    created_by=workflow_detail.updated_by,
                    created_at=workflow_detail.updated_at,
                    history_created_at =datetime.now(),
                    history_created_by = user
                )
            
            for key, value in request.POST.items():
                if key.startswith("action_field_") and not key.startswith("action_field_id_"):
                    match = re.match(r'action_field_(\d+)', key)
                    if match:
                        field_id = int(match.group(1))
                        action_field = get_object_or_404(FormActionField, pk=field_id)
                        if action_field.type in ['text', 'textarea', 'select']:
                            ActionData.objects.create(
                                value=value,
                                form_data=form_data,
                                field=action_field,
                                step_id=step_id,
                                created_by=user,
                                updated_by=user,
                            )

            messages.success(request, "Workflow data saved successfully!")

    except Exception as e:
        traceback.print_exc()
        messages.error(request, 'Oops...! Something went wrong!')

    finally:
        if role_id == '7':
            return redirect('candidate_index')
        else:
            return redirect('test_index')


def common_form_edit(request):

    user = request.session.get('user_id', '')
    workflow_YN = request.POST.get("workflow_YN")
    edit_type = request.POST.get("edit_type")
    
    
    try:
        if request.method != "POST":
            return JsonResponse({"error": "Invalid request method"}, status=400)

        form_data_id = request.POST.get("form_data_id")
        if not form_data_id:
            return JsonResponse({"error": "form_data_id is required"}, status=400)
        type = request.POST.get("type")
        
        form = get_object_or_404(Form, id=request.POST.get("form_id"))

        module_id = form.module
        module_tables = common_module_master(module_id)

        IndexTable = apps.get_model('Form', module_tables["index_table"])
        DataTable = apps.get_model('Form', module_tables["data_table"])
        FileTable = apps.get_model('Form', module_tables["file_table"])

        form_data = get_object_or_404(IndexTable, id=form_data_id)
        form_data.updated_by = user
        form_data.save()

        form = get_object_or_404(Form, id=request.POST.get("form_id"))

        created_by = request.session.get("user_id", "").strip()
        form_name = request.POST.get("form_name", "").strip()
    

        # Re-create all non-file fields
        for key, value in request.POST.items():
            if key.startswith("field_id_"):
                field_id = value.strip()
                field = get_object_or_404(FormField, id=field_id)

                if field.field_type == "select multiple"  or field.field_type == "multiple":
                    selected_values = request.POST.getlist(f"field_{field_id}")
                    input_value = ','.join([val.strip() for val in selected_values if val.strip()])
                else:
                    input_value = request.POST.get(f"field_{field_id}", "").strip()

                if field.field_type == "generative":
                    continue
                elif  field.field_type in ["file", "file multiple"]:
                    continue

                # Check if a value already exists for this field
                existing_value = DataTable.objects.filter(
                    form_data=form_data, form=form, field=field
                ).first()

                if existing_value:
                    # Update existing entry
                    existing_value.value = input_value
                    existing_value.save()
                else:
                    # Create new entry
                    DataTable.objects.create(
                        form_data=form_data,
                        form=form,
                        field=field,
                        value=input_value,
                        created_by=created_by
                    )



        # ✅ File upload logic goes here
        handle_uploaded_files(request, form_name, created_by, form_data, user,module_id)
        messages.success(request, "Form data updated successfully!")
        if workflow_YN == '1E':
            wfdetailsid = request.POST.get('wfdetailsid', '')
            role_idC = request.POST.get('role_id', '')
            form_id = request.POST.get('form_id', '')
            step_id = request.POST.get('step_id', '')
            if wfdetailsid and wfdetailsid != 'undefined':
                wfdetailsid=dec(wfdetailsid)
            else:
                wfdetailsid = None  
            
            if step_id:
                matrix_entry = workflow_matrix.objects.filter(id=step_id).first()
                if matrix_entry:
                    status_from_matrix = matrix_entry.status  # adjust field name if needed
                    
            if form_data_id and rec_workflow_details.objects.filter(form_data_id=form_data_id).exists():
                # Update existing record
                workflow_detail = rec_workflow_details.objects.get(form_data_id=form_data_id)
                workflow_detail.form_data_id = form_data_id
                workflow_detail.role_id = request.POST.get('role_id', '')
                workflow_detail.action_details_id = request.POST.get('action_id', '')
                workflow_detail.step_id = request.POST.get('step_id', '')
                workflow_detail.increment_id += 1
                workflow_detail.status = status_from_matrix or ''
                workflow_detail.updated_at = datetime.now()
                workflow_detail.updated_by = user 
                workflow_detail.save()    
            else:    
                workflow_detail = rec_workflow_details.objects.create(
                form_data_id=form_data_id,
                role_id=request.POST.get('role_id', ''),
                action_details_id=request.POST.get('action_id', ''),
                increment_id=1,
                form_id=request.POST.get('form_id', ''),
                action_id=request.POST.get('action_id', ''),
                status = status_from_matrix or '',
                step_id=request.POST.get('step_id', ''),
                # user_id=user,
                created_at = datetime.now(),
                created_by=user,
                updated_by = user,
                
                )

            # Now set and save req_id using the generated ID
            workflow_detail.req_id = f"REQNO-00{workflow_detail.id}"
            workflow_detail.save()
            if wfdetailsid and rec_workflow_details.objects.filter(id=wfdetailsid).exists():
                rec_history_workflow_details.objects.create(
                    form_data_id=workflow_detail.form_data_id,
                    role_id=workflow_detail.role_id,
                    action_details_id=workflow_detail.action_details_id,
                    increment_id=workflow_detail.increment_id,
                    step_id=workflow_detail.step_id,
                    status=workflow_detail.status,
                    # user_id=workflow_detail.user_id,
                    # req_id=workflow_detail.req_id,
                    form_id=request.POST.get('form_id', ''),
                    created_by=workflow_detail.updated_by,
                    created_at=workflow_detail.updated_at,
                    history_created_at =datetime.now(),
                    history_created_by = user
                )
            else:
                rec_history_workflow_details.objects.create(
                    form_data_id=workflow_detail.form_data_id,
                    role_id=workflow_detail.role_id,
                    action_details_id=workflow_detail.action_details_id,
                    increment_id=workflow_detail.increment_id,
                    step_id=workflow_detail.step_id,
                    status=workflow_detail.status,
                    # user_id=workflow_detail.user_id,
                    # req_id=workflow_detail.req_id,
                    # operator=request.POST.get('custom_dropdownOpr', ''),
                    form_id=request.POST.get('form_id', ''),
                    created_by=workflow_detail.updated_by,
                    created_at=workflow_detail.updated_at,
                    history_created_at =datetime.now(),
                    history_created_by = user
                )
                
            
            messages.success(request, "Workflow data saved successfully!")

    except Exception as e:
        traceback.print_exc()
        messages.error(request, "Oops...! Something went wrong!")

    finally:
        #return redirect("/masters?entity=form_master&type=i")
        # if workflow_YN == '1E':
        #     return redirect('workflow_starts')
        if edit_type == 'edit_type':
            return redirect('candidate_index')
        elif type == 'edit':
            return redirect('test_index')
        else:
            return redirect("/masters?entity=form_master&type=i")

    

def handle_uploaded_files(request, form_name, created_by, form_data, user,module_id):
    try:
        for field_key, uploaded_files in request.FILES.lists():
            if not field_key.startswith("field_"):
                continue

            field_id = field_key.split("_")[-1].strip()
            field = get_object_or_404(FormField, id=field_id)

            module_tables = common_module_master(module_id)

            IndexTable = apps.get_model('Form', module_tables["index_table"])
            DataTable = apps.get_model('Form', module_tables["data_table"])
            FileTable = apps.get_model('Form', module_tables["file_table"])

            file_dir = os.path.join(settings.MEDIA_ROOT, form_name, created_by, form_data.req_no)
            os.makedirs(file_dir, exist_ok=True)

            is_multiple = field.field_type == "file multiple"

            for uploaded_file in uploaded_files:
                uploaded_file_name = uploaded_file.name.strip()
                original_file_name, file_extension = os.path.splitext(uploaded_file_name)
                timestamp = timezone.now().strftime('%Y%m%d%H%M%S%f')
                saved_file_name = f"{original_file_name}_{timestamp}{file_extension}"
                save_path = os.path.join(file_dir, saved_file_name)
                relative_file_path = os.path.join(form_name, created_by, form_data.req_no, saved_file_name)

                if is_multiple:
                    # Check if this file name already exists
                    existing_file = FileTable.objects.filter(
                        form_data=form_data,
                        field=field,
                        uploaded_name=uploaded_file_name
                    ).first()

                    if existing_file:
                        old_file_path = os.path.join(settings.MEDIA_ROOT, existing_file.file_path)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)

                        with open(save_path, 'wb+') as destination:
                            for chunk in uploaded_file.chunks():
                                destination.write(chunk)

                        existing_file.file_name = saved_file_name
                        existing_file.file_path = relative_file_path
                        existing_file.updated_by = user
                        existing_file.save()
                        continue

                else:
                    # 🔥 Single file logic: Delete old one (if any) for this field + form_data
                    existing_files = FileTable.objects.filter(form_data=form_data, field=field)
                    for old_file in existing_files:
                        old_file_path = os.path.join(settings.MEDIA_ROOT, old_file.file_path)
                        if os.path.exists(old_file_path):
                            os.remove(old_file_path)
                        old_file.delete()

                # Save new file
                with open(save_path, 'wb+') as destination:
                    for chunk in uploaded_file.chunks():
                        destination.write(chunk)

                form_file = FileTable.objects.create(
                    file_name=saved_file_name,
                    uploaded_name=uploaded_file_name,
                    file_path=relative_file_path,
                    form_data=form_data,
                    form=form_data.form,
                    created_by=user,
                    updated_by=user,
                    field=field
                )
                 
                form_field_value = DataTable.objects.filter(
                    form_id=form_data.form.id,
                    field_id=field.id,
                    form_data = form_data
                ).first()

                if form_field_value:
                    # 3. Update values (append or set)
                    if form_field_value.value:
                        # Already has value, so append new id
                        existing_ids = form_field_value.value.split(',')
                        existing_ids.append(str(form_file.id))
                        form_field_value.value = ','.join(existing_ids)
                    else:
                        # No value yet, set directly
                        form_field_value.value = str(form_file.id)

                    form_field_value.save()

                    # 4. Update FormFile to add file_id (which is FormFieldValues' id)
                    form_file.file_id = form_field_value.id
                    form_file.save()



    except Exception as e:
        traceback.print_exc()
        messages.error(request, "Oops...! Something went wrong!")



def form_preview(request):
    id = request.GET.get("id")
    id = dec(id)  

    if not id:
        return render(request, "Form/_formfields.html", {"forms_data": []})

    try:
        workflow = get_object_or_404(workflow_matrix, id=id)
        form_ids = workflow.form_id.split(",")  # Multiple form IDs
        action_id = workflow.button_type_id

        forms_data = []

        action_fields = list(FormActionField.objects.filter(action_id=action_id).values(
                "id", "type", "label_name", "button_name", "bg_color", "text_color", 
                "button_type", "dropdown_values", "status", "action_id"
            ))
        
        for action in action_fields:
            action["dropdown_values"] = action["dropdown_values"].split(",") if action["dropdown_values"] else []

        for form_id in form_ids:
            form_id = form_id.strip()
            if not form_id:
                continue

            form = get_object_or_404(Form, id=form_id)

            raw_fields = FormField.objects.filter(form_id=form_id).values(
                "id", "label", "field_type", "values", "attributes", "form_id", "form_id__name", "section"
            ).order_by("order")


            sectioned_fields = {}

            for field in raw_fields:
                field["values"] = [v.strip() for v in field["values"].split(",")] if field.get("values") else []
                field["attributes"] = [a.strip() for a in field["attributes"].split(",")] if field.get("attributes") else []

                section_id = field.get("section")
                if section_id:
                    try:
                        section = SectionMaster.objects.get(id=section_id)
                        section_name = section.name
                    except SectionMaster.DoesNotExist:
                        section_name = ""
                else:
                    section_name = ""

                field["section_name"] = section_name

                validations = FieldValidation.objects.filter(
                    field_id=field["id"], form_id=form_id
                ).values("value")
                field["validations"] = list(validations)

                if any("^" in v["value"] for v in field["validations"]):
                    field["field_type"] = "regex"
                    pattern_value = field["validations"][0]["value"]
                    try:
                        regex_obj = RegexPattern.objects.get(regex_pattern=pattern_value)
                        field["regex_id"] = regex_obj.id
                        field["regex_description"] = regex_obj.description
                    except RegexPattern.DoesNotExist:
                        field["regex_id"] = None
                        field["regex_description"] = ""

                if field["field_type"] in ["file", "file multiple", "text"]:
                    file_validation = next((v for v in field["validations"]), None)
                    field["accept"] = file_validation["value"] if file_validation else ""

                if field["field_type"] == "field_dropdown":
                    split_values = field["values"]
                    if len(split_values) == 2:
                        dropdown_form_id, dropdown_field_id = split_values
                        field_values = FormFieldValues.objects.filter(field_id=dropdown_field_id).values("value").distinct()
                        field["dropdown_data"] = list(field_values)

                if field["field_type"] in ["master dropdown", "multiple"] and field["values"]:
                    dropdown_id = field["values"][0]
                    try:
                        master_data = MasterDropdownData.objects.get(id=dropdown_id)
                        query = master_data.query
                        result = callproc("stp_get_query_data", [query])
                        field["values"] = [{"id": row[0], "name": row[1]} for row in result]
                    except MasterDropdownData.DoesNotExist:
                        field["values"] = []

                sectioned_fields.setdefault(section_name, []).append(field)

            forms_data.append({
                "form": form,
                "sectioned_fields": sectioned_fields,
            })

        return render(request, "Form/_formfieldedit.html", {
            "matrix_id": id,
            "forms_data": forms_data,
            "action_fields": action_fields,
            "type": "create"
        })

    except Exception as e:
        traceback.print_exc()
        messages.error(request, "Oops...! Something went wrong!")
        return render(request, "Form/_formfields.html", {"fields": []})

    


def common_form_action(request):
    user = request.session.get('user_id', '')
    try:
        if request.method == 'POST':
            form_data_id = request.POST.get('form_data_id')
            form_data = get_object_or_404(FormData, pk=form_data_id)
            button_type = request.POST.get('button_type')
            clicked_action_id = request.POST.get('clicked_action_id')
            
            # Process only if it's an Action button
            if button_type == 'Action':
                clicked_action_id = request.POST.get('clicked_action_id')
                if clicked_action_id:
                    try:
                        clicked_action_id = int(clicked_action_id)
                    except ValueError:
                        messages.error(request, "Invalid action button identifier.")
                        return redirect('/masters?entity=form_master&type=i')
                    
                    # Save the clicked action button with its status
                    action_field = get_object_or_404(FormActionField, pk=clicked_action_id)
                    if action_field.button_type == 'Action':
                        ActionData.objects.create(
                            value=action_field.status,  # saving the status from FormActionField
                            form_data=form_data,
                            field=action_field,
                            created_by=user,
                            updated_by=user,
                        )
                
                # Now process the non-button fields (text, textarea, dropdown)
                for key, value in request.POST.items():
                    if key.startswith("action_field_") and not key.startswith("action_field_id_"):
                        # Extract the numeric ID using a regular expression to avoid non-integer parts
                        match = re.match(r'action_field_(\d+)', key)
                        if match:
                            field_id = int(match.group(1))
                            action_field = get_object_or_404(FormActionField, pk=field_id)
                            if action_field.type in ['text', 'textarea', 'dropdown']:
                                ActionData.objects.create(
                                    value=value,
                                    form_data=form_data,
                                    field=action_field,
                                    created_by=user,
                                    updated_by=user,
                                )
            messages.success(request, "Action data saved successfully!")
        
        return redirect('/masters?entity=form_master&type=i')
    
    except Exception as e:
        traceback.print_exc()
        messages.error(request, "Oops...! Something went wrong!")
        return redirect('/masters?entity=form_master&type=i')



def download_file(request):
    try:
        encrypted_path = request.GET.get('file')
        if not encrypted_path:
            raise Http404("Missing file parameter")

        # Decrypt to get file_path
        filepath = dec(encrypted_path)  # This should match the `file_path` in the DB
        full_path = os.path.join(settings.MEDIA_ROOT, filepath)

        if not os.path.exists(full_path):
            raise Http404("File does not exist")

        # Lookup uploaded name from DB using file_path
        try:
            file_obj = FormFile.objects.get(file_path=filepath)
            uploaded_name = file_obj.uploaded_name
        except FormFile.DoesNotExist:
            uploaded_name = os.path.basename(filepath)  # fallback

        response = FileResponse(open(full_path, 'rb'), as_attachment=True, filename=uploaded_name)
        return response

    except Exception as e:
        raise Http404("Invalid or corrupted file path")
    
def delete_file(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            enc_id = data.get("id")
            enc_path = data.get("path")

            file_id = dec(enc_id)
            file_path = dec(enc_path)

            # Delete the file record
            form_file = FormFile.objects.get(id=file_id)
            full_path = os.path.join(settings.MEDIA_ROOT, file_path)

            if os.path.exists(full_path):
                os.remove(full_path)

            form_file.delete()

            return JsonResponse({"success": True})
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({"success": False, "error": "Could not delete file"}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)



def handle_generative_fields(form, form_data, created_by,module_id):
    generative_fields = FormField.objects.filter(form=form, field_type="generative")

    for field in generative_fields:
        try:
            gen_settings = FormGenerativeField.objects.get(field=field, form=form)

            prefix = gen_settings.prefix or ''
            selected_ids = (gen_settings.selected_field_id or '').split(',')
            no_of_zero = int(gen_settings.no_of_zero or '0')
            initial_increment = int(gen_settings.increment or '1')

            module_tables = common_module_master(module_id)

            IndexTable = apps.get_model('Form', module_tables["index_table"])
            DataTable = apps.get_model('Form', module_tables["data_table"])
            FileTable = apps.get_model('Form', module_tables["file_table"])

            increment_row, created = FormIncrementNo.objects.get_or_create(
                form=form,
                defaults={'increment': initial_increment}
            )

            if not created:
                increment_row.increment += 1
                increment_row.save()

            current_increment = increment_row.increment

            # Step 1: Gather selected field values and filter out blanks
            selected_values = []
            for sel_id in selected_ids:
                sel_id = sel_id.strip()
                
                if not sel_id.isdigit():  
                    continue

                selected_field = FormField.objects.filter(id=int(sel_id)).first()
                if not selected_field:
                    continue

                value_obj = DataTable.objects.filter(
                    form_data=form_data,
                    form=form,
                    field=selected_field
                ).first()

                if value_obj and value_obj.value.strip():
                    selected_values.append(value_obj.value.strip())


                value_obj = DataTable.objects.filter(
                    form_data=form_data,
                    form=form,
                    field=selected_field
                ).first()

                if value_obj and value_obj.value.strip():  # Check for non-empty values
                    selected_values.append(value_obj.value.strip())

            # Step 2: Construct base part
            base_part = '-'.join(selected_values)

            # Step 3: Construct final value smartly
            padded_number = str(0).zfill(no_of_zero)
            parts = []

            if prefix.strip():
                parts.append(prefix.strip())
            if base_part:
                parts.append(base_part)
            parts.append(f"{padded_number}{current_increment}")

            final_value = '_'.join(parts)

            field_obj = get_object_or_404(FormField, id=field.id)
            primary = 1 if field_obj.is_primary == 1 else 0

            # Step 4: Save the generated value
            DataTable.objects.create(
                form_data=form_data,
                form=form,
                field=field,
                primary_key=primary,
                value=final_value,
                created_by=created_by
            )
            # form_data = get_object_or_404(IndexTable, id = form_data.id)
            form_data.candidate_id = final_value
            form_data.save()

        except Exception as e:
            traceback.print_exc()
        
        return final_value

        



def get_uploaded_files(request):
    try:
        field_id = request.POST.get("field_id")
        form_data_id = request.POST.get("form_data_id")
        form_id = request.POST.get("form_id")

        module_id = get_object_or_404(Form, id = form_id).module
        module_tables = common_module_master(module_id)

        IndexTable = apps.get_model('Form', module_tables["index_table"])
        DataTable = apps.get_model('Form', module_tables["data_table"])
        FileTable = apps.get_model('Form', module_tables["file_table"])

        files = FileTable.objects.filter(
            field_id=field_id,
            form_data_id=form_data_id
        )

        file_list = []
        for f in files:
            full_path = os.path.join(settings.MEDIA_ROOT, f.file_path)
            exists = os.path.exists(full_path)

            file_id = enc(str(f.id))  # Use current file's ID

            if exists:
                encrypted_url = enc(f.file_path)
                status = 1
            else:
                encrypted_url = ''
                status = 0

            file_list.append({
                'name': f.uploaded_name,
                'status': status,
                'encrypted_url': encrypted_url,
                'file_id': file_id  # Correctly encrypted ID for each file
            })

        return JsonResponse({'files': file_list})

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({'error': 'Something went wrong while fetching files'}, status=500)
        
def get_query_data(request):
    if request.method == "POST":
        try:
            id = request.POST.get("query")
            # id = dec(id)
            query = get_object_or_404(MasterDropdownData, id= id).query
            data = callproc("stp_get_query_data",[query])
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

@csrf_exempt
def check_field_before_delete(request):
    if request.method == "POST":
        field_id = request.POST.get("field_id")

        if  not field_id:
            return JsonResponse({"success": False, "error": "Missing form or field ID."})

        data_exists = FormFieldValues.objects.filter(field_id=field_id).exists()

        if data_exists:
            return JsonResponse({"exists": True})  # Indicates data is present; can't delete
        else:
            return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request method."})


def get_regex_pattern(request):
    if request.method == "POST":
        regex_id = request.POST.get("regex_id")

        try:
            regex = RegexPattern.objects.get(id=regex_id)
            return JsonResponse({
                "regex_id":regex_id,
                "pattern": regex.regex_pattern,
                "description": regex.description
            })
        except RegexPattern.DoesNotExist:
            return JsonResponse({"error": "Pattern not found"}, status=404)

    return JsonResponse({"error": "Invalid request method"}, status=400)


def create_new_section(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            # Check for duplicate (case insensitive)
            existing_section = SectionMaster.objects.filter(name__iexact=name).first()
            if existing_section:
                return JsonResponse({
                    "id": existing_section.id,
                    "name": existing_section.name,
                    "message": "Section already exists"
                })
            
            # Create new section if not exists
            section = SectionMaster.objects.create(name=name)
            return JsonResponse({
                "id": section.id,
                "name": section.name,
                "message": "Section created"
            })
    return JsonResponse({"error": "Invalid request"}, status=400)

def get_field_names(request):
    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        fields = FormField.objects.filter(form_id=form_id).values('id', 'label')
        return JsonResponse({'fields': list(fields)})
    

def show_form(request):
    user  = request.session.get('user_id', '')
    role = str(request.session.get('role_id'))
    form_data = request.GET.get('form')
    if form_data:
        form_data_id = dec(form_data)
    try: 
        if form_data:
            step_id = 2

            workflows = workflow_matrix.objects.filter(step_id_flow= 2)

            workflow = None
            for wf in workflows:
                role_ids = [r.strip() for r in wf.role_id.split(',')]
                if role in role_ids:
                    workflow = wf
                    break

            if not workflow:
                return JsonResponse({"error": "No workflow found for role"}, status=400)

            form_ids = workflow.form_id.split(",")
            action_id = workflow.button_type_id
            first_form_id = form_ids[0]
            module = get_object_or_404(Form, id=first_form_id).module
            module_tables = common_module_master(module)
            

            IndexTable = apps.get_model('Form', module_tables["index_table"])
            DataTable = apps.get_model('Form', module_tables["data_table"])
            FileTable = apps.get_model('Form', module_tables["file_table"])

            form_data = IndexTable.objects.filter(id = form_data_id)
            

            # Get saved field values for this form_data (index ID)
            field_values = DataTable.objects.filter(form_data_id=form_data_id).values("field_id", "value")
            values_dict = {fv["field_id"]: fv["value"] for fv in field_values}

            # Get action fields
            action_fields = list(FormActionField.objects.filter(action_id=action_id).values(
                "id", "type", "label_name", "button_name", "bg_color", "text_color",
                "button_type", "dropdown_values", "status", "action_id"
            ))
            for action in action_fields:
                action["dropdown_values"] = action["dropdown_values"].split(",") if action["dropdown_values"] else []

            forms_data = []

            for form_id in form_ids:
                form_id = form_id.strip()
                if not form_id:
                    continue

                form = get_object_or_404(Form, id=form_id)
                

                raw_fields = FormField.objects.filter(form_id=form_id).values(
                    "id", "label", "field_type", "values", "attributes", "form_id", "form_id__name", "section"
                ).order_by("order")

                sectioned_fields = {}

                for field in raw_fields:
                    field_id = field["id"]
                    field["values"] = field["values"].split(",") if field.get("values") else []
                    field["attributes"] = field["attributes"].split(",") if field.get("attributes") else []

                    # Section name
                    section_id = field.get("section")
                    if section_id:
                        try:
                            section = SectionMaster.objects.get(id=section_id)
                            section_name = section.name
                        except SectionMaster.DoesNotExist:
                            section_name = ""
                    else:
                        section_name = ""
                    field["section_name"] = section_name

                    # Validations
                    validations = FieldValidation.objects.filter(
                        field_id=field_id, form_id=form_id
                    ).values("value")
                    field["validations"] = list(validations)

                    if any("^" in v["value"] for v in field["validations"]):
                        field["field_type"] = "regex"
                        pattern_value = field["validations"][0]["value"]
                        try:
                            regex_obj = RegexPattern.objects.get(regex_pattern=pattern_value)
                            field["regex_id"] = regex_obj.id
                            field["regex_description"] = regex_obj.description
                        except RegexPattern.DoesNotExist:
                            field["regex_id"] = None
                            field["regex_description"] = ""

                    if field["field_type"] in ["file", "file multiple", "text"]:
                        file_validation = next((v for v in field["validations"]), None)
                        field["accept"] = file_validation["value"] if file_validation else ""

                        file_exists = FileTable.objects.filter(field_id=field_id, form_data_id=form_data_id).exists()
                        field["file_uploaded"] = 1 if file_exists else 0

                        if file_exists and "required" in field["attributes"]:
                            field["attributes"].remove("required")

                    # Set saved value
                    saved_value = values_dict.get(field_id, "")
                    if field["field_type"] == "select multiple":
                        field["value"] = [val.strip() for val in saved_value.split(",") if val.strip()]
                    else:
                        field["value"] = saved_value

                    # Field Dropdown (Linked dropdowns)
                    if field["field_type"] == "field_dropdown":
                        split_values = field["values"]
                        if len(split_values) == 2:
                            try:
                                dropdown_field_id = int(split_values[1])
                                dropdown_field_values = DataTable.objects.filter(field_id=dropdown_field_id).values("value")
                                field["dropdown_data"] = list(dropdown_field_values)
                            except (ValueError, IndexError):
                                field["dropdown_data"] = []

                    # Master Dropdown / Multiple from master table
                    if field["field_type"] in ["master dropdown", "multiple"] and field["values"]:
                        try:
                            dropdown_id = field["values"][0]
                            master_data = MasterDropdownData.objects.get(id=dropdown_id)
                            query = master_data.query
                            result = callproc("stp_get_query_data", [query])
                            field["values"] = [{"id": row[0], "name": row[1]} for row in result]
                        except (MasterDropdownData.DoesNotExist, IndexError):
                            field["values"] = []

                    # Group fields by section
                    sectioned_fields.setdefault(section_name, []).append(field)

                forms_data.append({
                    "form": form,
                    "sectioned_fields": sectioned_fields,
                })

            return render(request, "Form/_formfieldedit.html", {
                "matrix_id": id,
                "forms_data": forms_data,
                "action_fields": action_fields,
                "type": "edit",
                "form":form,
                "form_data": form_data,
                "form_data_id":form_data_id,
                "step_id":step_id,
                "workflow_YN":"1E",
                "action":action,
            })


        else:  
            step_id=1
            workflows = workflow_matrix.objects.filter(step_id_flow=step_id)

            workflow = None
            for wf in workflows:
                role_ids = [r.strip() for r in wf.role_id.split(',')]
                if role in role_ids:
                    workflow = wf
                    
                form_ids = workflow.form_id.split(",") 
                action_id = workflow.button_type_id

                forms_data = []

                action_fields = list(FormActionField.objects.filter(action_id=action_id).values(
                        "id", "type", "label_name", "button_name", "bg_color", "text_color", 
                        "button_type", "dropdown_values", "status", "action_id"
                    ))
        
                for action in action_fields:
                    action["dropdown_values"] = action["dropdown_values"].split(",") if action["dropdown_values"] else []

                for form_id in form_ids:
                    form_id = form_id.strip()
                    if not form_id:
                        continue

                    form = get_object_or_404(Form, id=form_id)

                    raw_fields = FormField.objects.filter(form_id=form_id).values(
                        "id", "label", "field_type", "values", "attributes", "form_id", "form_id__name", "section"
                    ).order_by("order")


                    sectioned_fields = {}

                    for field in raw_fields:
                        field["values"] = [v.strip() for v in field["values"].split(",")] if field.get("values") else []
                        field["attributes"] = [a.strip() for a in field["attributes"].split(",")] if field.get("attributes") else []

                        section_id = field.get("section")
                        if section_id:
                            try:
                                section = SectionMaster.objects.get(id=section_id)
                                section_name = section.name
                            except SectionMaster.DoesNotExist:
                                section_name = ""
                        else:
                            section_name = ""

                        field["section_name"] = section_name

                        validations = FieldValidation.objects.filter(
                            field_id=field["id"], form_id=form_id
                        ).values("value")
                        field["validations"] = list(validations)

                        if any("^" in v["value"] for v in field["validations"]):
                            field["field_type"] = "regex"
                            pattern_value = field["validations"][0]["value"]
                            try:
                                regex_obj = RegexPattern.objects.get(regex_pattern=pattern_value)
                                field["regex_id"] = regex_obj.id
                                field["regex_description"] = regex_obj.description
                            except RegexPattern.DoesNotExist:
                                field["regex_id"] = None
                                field["regex_description"] = ""

                        if field["field_type"] in ["file", "file multiple", "text"]:
                            file_validation = next((v for v in field["validations"]), None)
                            field["accept"] = file_validation["value"] if file_validation else ""

                        if field["field_type"] == "field_dropdown":
                            split_values = field["values"]
                            if len(split_values) == 2:
                                dropdown_form_id, dropdown_field_id = split_values
                                field_values = FormFieldValues.objects.filter(field_id=dropdown_field_id).values("value").distinct()
                                field["dropdown_data"] = list(field_values)

                        if field["field_type"] in ["master dropdown", "multiple"] and field["values"]:
                            dropdown_id = field["values"][0]
                            try:
                                master_data = MasterDropdownData.objects.get(id=dropdown_id)
                                query = master_data.query
                                result = callproc("stp_get_query_data", [query])
                                field["values"] = [{"id": row[0], "name": row[1]} for row in result]
                            except MasterDropdownData.DoesNotExist:
                                field["values"] = []

                        sectioned_fields.setdefault(section_name, []).append(field)

                    forms_data.append({
                        "form": form,
                        "sectioned_fields": sectioned_fields,
                    })

                return render(request, "Form/_formfieldedit.html", {
                    "matrix_id": id,
                    "forms_data": forms_data,
                    "action_fields": action_fields,
                    "type": "create",
                    "form":form,
                    "action":action,
                    "step_id":step_id,
                    "workflow_YN":"1"
                })
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        print(e)
        callproc("stp_error_log", [fun, str(e), user])
        messages.error(request, 'Oops...! Something went wrong!')
        return JsonResponse({"error": "Something went wrong!"}, status=500)
    