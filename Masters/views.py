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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from Account.models import *
from Masters.models import *
from Account.db_utils import callproc
from django.views.decorators.csrf import csrf_exempt
import os
from django.urls import reverse
from THRMS.settings import *
import logging
from django.http import FileResponse, Http404
import mimetypes

from Workflow.models import workflow_action_master
logger = logging.getLogger(__name__)


# utils/ocr_utils.py

import pytesseract
from pdf2image import convert_from_path
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import os
import tempfile
import string

def extract_text_from_pdf(pdf_path):
    # Convert PDF to images
    # images = convert_from_path(pdf_path, poppler_path=r'C:\poppler\poppler-24.08.0\Library\bin')
    # ✅ On Linux, no need to set path if tesseract and poppler-utils are installed globally
    images = convert_from_path(pdf_path)

    full_text = ""
    # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    for image in images:
        text = pytesseract.image_to_string(image)
        full_text += text + "\n"
    
    return full_text.strip()

def extract_keywords(text, num_keywords=100):
    stop_words = set(stopwords.words('english'))
    from nltk.tokenize import word_tokenize
    words = word_tokenize(text.lower())

    words = [w for w in words if w.isalpha() and w not in stop_words]
    
    # Frequency distribution
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    
    sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    top_keywords = [kw for kw, _ in sorted_keywords[:num_keywords]]
    return top_keywords


import os
from django.shortcuts import render, redirect
from .models import Document
from django.core.files.storage import FileSystemStorage
from django.conf import settings

def upload_document(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        pdf_file = request.FILES.get('pdf_file')

        if title and pdf_file:
            # Save file to media/documents/
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'documents'))
            filename = fs.save(pdf_file.name, pdf_file)
            file_path = os.path.join(fs.location, filename)

            # OCR + Keyword extraction
            text = extract_text_from_pdf(file_path)
            keywords = extract_keywords(text)

            # Save to DB
            document = Document.objects.create(
                title=title,
                pdf_file=os.path.join('documents', filename),
                extracted_text=text,
                keywords=', '.join(keywords)
            )
            return redirect('document_detail', pk=document.pk)
    
    return render(request, 'Master/upload.html')



from django.shortcuts import get_object_or_404

def document_detail(request, pk):
    document = get_object_or_404(Document, pk=pk)
    return render(request, 'Master/document_detail.html', {'document': document})

@login_required
def masters(request):
    pre_url = request.META.get('HTTP_REFERER')
    header, data = [], []
    entity = type = name = id = text_name = dpl = dp = em = mb = forms = sf = ''
    try:
        if request.user.is_authenticated ==True:                
                global user,role_id
                user = request.user.id    
                role_id = request.user.role_id 
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            sf = request.GET.get('sf', '')
            type = request.GET.get('type', '')
            datalist1= callproc("stp_get_masters",[entity,type,'name',user])
            name = datalist1[0][0]
            header = callproc("stp_get_masters", [entity, type, 'header',user])
            rows = callproc("stp_get_masters",[entity,type,'data',user])
            if entity == 'form_master':
                forms = callproc("stp_get_forms",['view_form'])  
                type = 'i'
                if sf == '' or None:
                   sf =  forms[0][0]   
                header = callproc("stp_get_view_form_header",[sf])          
                rows = callproc("stp_get_view_forms",[sf])   
            if entity == 'su':
                dpl = callproc("stp_get_dropdown_values",['dept'])
            id = request.GET.get('id', '')
            if type=='ed' and id != '0':
                if id != '0' and id != '':
                    id = dec(id)
                rows = callproc("stp_get_masters",[entity,type,'data',id])
                text_name = rows[0][0]
                if entity == 'su':
                    em = rows[0][1]
                    mb = rows[0][2]
                    dp = rows[0][3]
                id = enc(id)
            data = []
            for row in rows:
                encrypted_id = enc(str(row[0]))
                data.append((encrypted_id,) + row[1:])

        if request.method=="POST":
            entity = request.POST.get('entity', '')
            id = request.POST.get('id', '')
            dp = request.POST.get('dp', '')
            em = request.POST.get('em', '')
            mb = request.POST.get('mb', '')
            if id != '0' and id != '':
                id = dec(id)
            name = request.POST.get('text_name', '')
            if entity == 'su':
                datalist1= callproc("stp_post_user_masters",[id,name,em,mb,dp,user])
            else: datalist1= callproc("stp_post_masters",[entity,id,name,user])

            if datalist1[0][0] == 'insert':
                messages.success(request, 'Data inserted successfully !')
            elif datalist1[0][0] == 'update':
                messages.success(request, 'Data updated successfully !')
            elif datalist1[0][0] == 'exist':
                messages.error(request, 'Data already exist !')
            
                          
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log",[fun,str(e),user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        Db.closeConnection()
        if request.method=="GET":
            return render(request,'Master/index.html',
              {'entity':entity,'type':type,'forms':forms,'sf':sf,'name':name,'header':header,'data':data,
              'id':id,'text_name':text_name,'dp':dp,'em':em,'mb':mb,'dpl':dpl})
        elif request.method=="POST":  
            new_url = f'/masters?entity={entity}&type=i'
            return redirect(new_url) 
 
def sample_xlsx(request):
    pre_url = request.META.get('HTTP_REFERER')
    response =''
    global user
    user  = request.session.get('user_id', '')
    try:
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.title = 'Sample Format'
        columns = []
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
        if request.method=="POST":
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
        file_name = {'em': 'Employee Master','sm': 'Worksite Master','cm': 'Company Master','r': 'Roster'}[entity]
        columns = callproc("stp_get_masters", [entity, type, 'sample_xlsx',user])
        if columns and columns[0]:
            columns = [col[0] for col in columns[0]]

        black_border = Border(
            left=Side(border_style="thin", color="000000"),
            right=Side(border_style="thin", color="000000"),
            top=Side(border_style="thin", color="000000"),
            bottom=Side(border_style="thin", color="000000")
        )
        
        for col_num, header in enumerate(columns, 1):
            cell = sheet.cell(row=1, column=col_num)
            cell.value = header
            cell.font = Font(bold=True)
            cell.border = black_border
        
        for col in sheet.columns:
            max_length = 0
            column = col[0].column_letter  
            for cell in col:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
                    
            adjusted_width = max_length + 2 
            sheet.column_dimensions[column].width = adjusted_width  
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="' + str(file_name) +" "+str(datetime.now().strftime("%d-%m-%Y")) + '.xlsx"'
        workbook.save(response)
    
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log",[fun,str(e),user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        return response      



    
def workflow_mapping(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    if request.user.is_authenticated ==True:                
                global user,role_id
                user = request.user.id    
                role_id = request.user.role_id
    try:
        if request.method == "GET":
            cursor.callproc("stp_getFormForMapping")
            for result in cursor.stored_results():
                form_dropdown = list(result.fetchall())
            cursor.callproc("stp_getButTypeForMapping")
            for result in cursor.stored_results():
                ButType_dropdown = list(result.fetchall())
            cursor.callproc("stp_getFormActForMapping")
            for result in cursor.stored_results():
                ButAct_dropdown = list(result.fetchall())
            cursor.callproc("stp_getworkflowD")
            for result in cursor.stored_results():
                workflow_dropdown = list(result.fetchall())
            cursor.callproc("stp_getRoleDD")
            for result in cursor.stored_results():
                role_dropdown = list(result.fetchall())
            cursor.callproc("stp_getEditCreateWFDD")
            for result in cursor.stored_results():
                wfEditCreate_dropdown = list(result.fetchall())
            # cursor.callproc("stp_getEditCrtForMapping")
            # for result in cursor.stored_results():
            #     EditCrt_dropdown = list(result.fetchall())
            getformdata = {'form_dropdown':form_dropdown,'ButType_dropdown':ButType_dropdown,
                           'ButAct_dropdown':ButAct_dropdown,'workflow_dropdown':workflow_dropdown,'role_dropdown':role_dropdown,"wfEditCreate_dropdown":wfEditCreate_dropdown,}
            return render(request, "Master/workflow_mapping.html",getformdata)
        
    except Exception as e:
        print("error-"+e)
        response_data = "fail"
        messages.error(request,"Some Error Occured !!")
    
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        
def get_actions_by_button_type(request):
    button_type_id = request.GET.get("button_type_id")
    
    # Fetch actions based on the button type ID using stored procedure or query
    actions = workflow_action_master.objects.filter(action_id=button_type_id).values("id", "action_details")

    return JsonResponse(list(actions), safe=False)

def decrypt_parameter(encoded_cipher_text):
    # Decode the base64-encoded string before decrypting
    cipher_text = base64.urlsafe_b64decode(encoded_cipher_text.encode())
    cipher_suite = Fernet(get_encryption_key())
    plain_text = cipher_suite.decrypt(cipher_text).decode()
    return plain_text

def submit_workflow(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    if request.user.is_authenticated ==True:                
                global user,role_id
                user = request.user.id    
                role_id = request.user.role_id
    try:
        workflow_name = request.POST.get("workflowDropdown")
        step_name = request.POST.get("stepName")
        form_name = request.POST.get("formDropdown")
        button_type = request.POST.get("buttonTypeDropdown")
        action = request.POST.get("actionDropdown")
        customRoleDropdown = request.POST.get("roles")
        param=(workflow_name,step_name,form_name,button_type,action,user,customRoleDropdown)
        cursor.callproc("stp_insertIntoWorkflow_matrix",param)   
        m.commit()  
        # return JsonResponse({"message": "Workflow submitted successfully!"}, status=200)
        return JsonResponse({"message": "Workflow submitted successfully!","redirect_url": "/masters/?entity=wfseq&type=i"}, status=200)

    except Exception as e:
            print("error-"+e)
            response_data = "fail"
            messages.error(request,"Some Error Occured !!")
        
    finally:
        cursor.close()        
        m.close()
        Db.closeConnection()
        
def workflow_Editmap(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()

    if request.user.is_authenticated:
        global user, role_id
        user = request.user.id
        role_id = request.user.role_id

    try:
        if request.method == "GET":
            workflow_idIncrypt = request.GET.get("wfseq_id")

            if workflow_idIncrypt:
                workflow_id = decrypt_parameter(workflow_idIncrypt) 
            
            param = [workflow_id] 

            
            cursor.callproc("stp_getFormForMapping")
            for result in cursor.stored_results():
                form_dropdown = list(result.fetchall())
            cursor.callproc("stp_getButTypeForMapping")
            for result in cursor.stored_results():
                ButType_dropdown = list(result.fetchall())
            cursor.callproc("stp_getFormActForMapping")
            for result in cursor.stored_results():
                ButAct_dropdown = list(result.fetchall())
            cursor.callproc("stp_getworkflowD")
            for result in cursor.stored_results():
                workflow_dropdown = list(result.fetchall())
            cursor.callproc("stp_getRoleDD")
            for result in cursor.stored_results():
                role_dropdown = list(result.fetchall())
            cursor.callproc("stp_getEditCreateWFDD")
            for result in cursor.stored_results():
                wfEditCreate_dropdown = list(result.fetchall())        
                  
            cursor.callproc("stp_getworkflowEdit", param)
            workflow_data = []
            for result in cursor.stored_results():
                workflow_data = result.fetchall()  
            
           
            workflow_details = {}
            if workflow_data:
                role_string = workflow_data[0][6]
                role_list = role_string.split(',') if role_string else []
                workflow_details = {
                    "workflow_name": workflow_data[0][0], 
                    "form_id": workflow_data[0][1],
                    "step_name": workflow_data[0][2],
                    "button_type_id": workflow_data[0][3],
                    "button_act_details": workflow_data[0][4],
                    "workflow_idD": workflow_data[0][5],
                    "role_id": role_string,
                    "role_list": role_list
                }

            getformdata = {
                    "form_dropdown": form_dropdown,
                    "ButType_dropdown": ButType_dropdown,
                    "ButAct_dropdown": ButAct_dropdown,
                    "workflow_dropdown": workflow_dropdown,
                    "workflow_details": workflow_details,
                    "role_dropdown":role_dropdown,
                    "workflow_id":workflow_idIncrypt,
                    "wfEditCreate_dropdown":wfEditCreate_dropdown,
                }

            return render(request, "Master/workflow_Editmap.html", getformdata)

        if request.method == "POST":
            workflow_idEncrypt = request.POST.get("workflow_idEncrypt")
            workflow_idDecryp = decrypt_parameter(workflow_idEncrypt)
            workflow_name = request.POST.get("workflowDropdown")
            step_name = request.POST.get("stepName")
            form_name = request.POST.get("formDropdown")
            button_type = request.POST.get("buttonTypeDropdown")
            action = request.POST.get("actionDropdown")
            roles = request.POST.get("roles")

            param = (workflow_name, step_name, form_name, button_type, action, workflow_idDecryp,user,roles)
            cursor.callproc("stp_updateWorkflow_matrix", param)
            m.commit()
            
            return JsonResponse({"message": "Workflow submitted successfully!","redirect_url": "/masters/?entity=wfseq&type=i"}, status=200)

    except Exception as e:
        print("Error:", e)
        messages.error(request, "Some Error Occurred !!")
        return JsonResponse({"message": "Error Occurred!"}, status=500)

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
