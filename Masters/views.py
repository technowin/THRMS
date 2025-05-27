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
from Masters.models import site_master as sit
from Masters.models import company_master as com
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
            return redirect('document_detail1', pk=document.pk)
    
    return render(request, 'Master/upload.html')



from django.shortcuts import get_object_or_404

def document_detail1(request, pk):
    document = get_object_or_404(Document, pk=pk)
    return render(request, 'Master/document_detail.html', {'document': document})

from django.shortcuts import render
from django.db.models import Q
from .models import Document

def search_documents(request):
    documents = Document.objects.all().order_by('-uploaded_at')
     # Process documents to add keywords_list
    def process_documents(docs):
        processed = []
        for doc in docs:
            processed.append({
                'id': doc.id,
                'title': doc.title,
                'pdf_file': doc.pdf_file,
                'keywords': doc.keywords,
                'uploaded_at': doc.uploaded_at,
                'keywords_list': doc.keywords.split(',') if doc.keywords else []
            })
        return processed
    context = {'documents': process_documents(documents),'search_type': None}
    if request.method == 'GET':
        # Simple search
        if 'simple_query' in request.GET:
            query = request.GET.get('simple_query', '').strip()
            if query:
                documents = documents.filter(
                    Q(title__icontains=query) | 
                    Q(keywords__icontains=query)
                )
                context['documents'] = process_documents(documents)
                context['search_type'] = 'simple'
                context['query'] = query
                context['show_results'] = True
        
        # Advanced search
        elif any(key in request.GET for key in ['title', 'keyword1', 'keyword2', 'keyword3']):
            title = request.GET.get('title', '').strip()
            keyword1 = request.GET.get('keyword1', '').strip()
            keyword2 = request.GET.get('keyword2', '').strip()
            keyword3 = request.GET.get('keyword3', '').strip()
            keyword4 = request.GET.get('keyword4', '').strip()
            keyword5 = request.GET.get('keyword5', '').strip()
            keyword6 = request.GET.get('keyword6', '').strip()
            match_all = request.GET.get('match_all', 'off') == 'on'
            if title or keyword1 or keyword2 or keyword3 or keyword4 or keyword5 or keyword6:
                documents = Document.objects.all()
                if title:
                    documents = documents.filter(title__icontains=title)

                keywords = [kw for kw in [keyword1, keyword2, keyword3, keyword4, keyword5, keyword6] if kw]
                if keywords:
                    if match_all:
                        for keyword in keywords:
                            documents = documents.filter(keywords__icontains=keyword)
                    else:
                        query = Q()
                        for keyword in keywords:
                            query |= Q(keywords__icontains=keyword)
                        documents = documents.filter(query)
                context['show_results'] = True

            context['documents'] = process_documents(documents)
            context['search_type'] = 'advanced'
            context['search_params'] = {'title': title,'keyword1': keyword1,'keyword2': keyword2,'keyword3': keyword3,'keyword4': keyword4,'keyword5': keyword5,'keyword6': keyword6,'match_all': match_all}

    
    return render(request, 'Master/search.html', context)

def document_detail(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    keywords = document.keywords.split(',')[:20]  # Top 20

    text = document.extracted_text
    for idx, keyword in enumerate(keywords):
        pattern = r'\b' + re.escape(keyword) + r'\b'
        span = f"<span class='kw kw{idx}'>{keyword}</span>"
        text = re.sub(pattern, span, text, flags=re.IGNORECASE)

    return render(request, 'Master/document_keyword.html', {
        'document': document,
        'keywords': keywords,
        'highlighted_text': text
    })

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
            company_names = callproc("stp_get_dropdown_values", ('company',))
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
            if entity == 'urm' and (type == 'acu' or type == 'acr'):
                header = callproc("stp_get_access_control",[entity,type])
                company_names = callproc("stp_get_access_control",[entity,'comp'])
                data = callproc("stp_get_access_control",[entity,'site'])

        if request.method=="POST":
            entity = request.POST.get('entity', '')
            id = request.POST.get('id', '')
            dp = request.POST.get('dp', '')
            em = request.POST.get('em', '')
            mb = request.POST.get('mb', '')
            type = request.POST.get('type', '')
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
            if entity == 'urm' and (type == 'acu' or type == 'acr'):
                try:
                    created_by = request.session.get('user_id', '')
                    ur = request.POST.get('ur', '')
                    selected_worksite = request.POST.getlist('worksite', [])
                    company_worksite_map = {}

                    # Validate input
                    if not selected_worksite:
                        messages.error(request, 'Worksite data is missing!')
                        return redirect(f'/masters?entity={entity}&type=urm')

                    if type not in ['acu', 'acr'] or not ur:
                        messages.error(request, 'Invalid data received.')
                        return redirect(f'/masters?entity={entity}&type=urm')

                    # Parse selected worksites into company-worksite pairs
                    selected_worksite_pairs = [
                        tuple(ws.split(" - ", 1)) for ws in selected_worksite if " - " in ws
                    ]
                    if not selected_worksite_pairs:
                        messages.error(request, 'Invalid worksite format. Expected "Company Name - Worksite Name".')
                        return redirect(f'/masters?entity={entity}&type=urm')

                    valid_combinations = []
                    for company_name, worksite_name in selected_worksite_pairs:
                        try:
                            # Fetch company_id using ORM
                            company = com.objects.get(company_name=company_name)
                            company_id = company.company_id
                        except com.DoesNotExist:
                            messages.error(request, f'Company "{company_name}" does not exist.')
                            continue

                        # Check if the worksite exists for the company in SiteMaster
                        if sit.objects.filter(company_id=company_id, site_name=worksite_name).exists():
                            valid_combinations.append((company_id, worksite_name))
                        else:
                            messages.error(request, f'Worksite "{worksite_name}" does not exist for company "{company_name}".')

                    if not valid_combinations:
                        messages.error(request, 'No valid company-worksite combinations found.')

                    # Remove existing mappings
                    callproc("stp_delete_access_control", [type, ur])

                    # Insert new mappings
                    insertion_status = "failure"
                    for company_id, worksite_name in valid_combinations:
                        insertion_status = callproc("stp_post_access_control", [type, ur, company_id, worksite_name, created_by])
                        

                    # Redirect based on insertion status
                    if insertion_status == "success":
                        messages.success(request, 'Data updated successfully!')
                    else:
                        messages.error(request, 'Oops...! Something went wrong!')
                except Exception as e:
                    tb = traceback.extract_tb(e.__traceback__)
                    fun = tb[0].name
                    callproc("stp_error_log",[fun,str(e),user])  
                    messages.error(request, 'Oops...! Something went wrong!')

                    
            else : messages.error(request, 'Oops...! Something went wrong!')
            
                          
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        callproc("stp_error_log",[fun,str(e),user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        Db.closeConnection()
        if request.method=="GET":
            return render(request,'Master/index.html',
              {'entity':entity,'type':type,'forms':forms,'sf':sf,'name':name,'header':header,'data':data,"company_names":company_names,
              'id':id,'text_name':text_name,'dp':dp,'em':em,'mb':mb,'dpl':dpl})
        elif request.method=="POST":  
            if entity == 'urm':
                new_url = f'/masters?entity={entity}&type=urm'
                return redirect(new_url)
            else:
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

def company_master(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    global user
    user  = request.session.get('user_id', '')
    try:
        
        if request.method == "GET":
        
            company_id = request.GET.get('id', '')
            if company_id == "0":
                if request.method == "GET":
                    context = {'company_id':company_id}
            else:
                company_id1 = request.GET.get('company_id', '')
                company_id= decrypt_parameter(company_id1)
                cursor.callproc("stp_edit_company_master", (company_id,))  # Note the comma to make it a tuple
                for result in cursor.stored_results():
                    data = result.fetchall()[0]  
                        
                    context = {
                        'company_id' : data[0],
                        'company_name': data[1],
                        'company_address': data[2],
                        'pincode': data[3],
                        'contact_person_name': data[4],
                        'contact_person_email': data[5], 
                        'contact_person_mobile_no': data[6],
                        'is_active':data[7]
                    }

        if request.method == "POST" :
            company_id = request.POST.get('company_id', '')
            if company_id == '0':
                response_data = {"status": "fail"}
                company_name = request.POST.get('company_name', '')
                company_address = request.POST.get('company_address', '')
                pincode = request.POST.get('pincode', '')
                contact_person_name = request.POST.get('contact_person_name', '')
                contact_person_email = request.POST.get('contact_person_email', '')
                contact_person_mobile_no = request.POST.get('contact_person_mobile_no', '') 
                # is_active = request.POST.get('status_value', '') 
                params = [
                    company_name, 
                    company_address, 
                    pincode, 
                    contact_person_name,
                    contact_person_email,
                    contact_person_mobile_no
                    # is_active
                ]
                cursor.callproc("stp_insert_company_master", params)
                for result in cursor.stored_results():
                        datalist = list(result.fetchall())
                if datalist[0][0] == "success":
                    messages.success(request, 'Data successfully entered !')
                else: messages.error(request, datalist[0][0])
            else :
                company_id = request.POST.get('company_id', '')
                company_name = request.POST.get('company_name', '')
                company_address = request.POST.get('company_address', '')
                pincode = request.POST.get('pincode', '')
                contact_person_name = request.POST.get('contact_person_name', '')
                contact_person_email = request.POST.get('contact_person_email', '')
                contact_person_mobile_no = request.POST.get('contact_person_mobile_no', '') 
                is_active = request.POST.get('status_value', '') 
                   
                params = [company_id,company_name,company_address,pincode,contact_person_name,contact_person_email,
                                            contact_person_mobile_no,is_active]    
                cursor.callproc("stp_update_company_master",params) 
                messages.success(request, "Data updated successfully ...!")
                
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()

        encrypted_id = enc(company_id)
            
        if request.method=="GET":
            return render(request, "Master/master/company_master.html", context)
        elif request.method == "POST":
            return redirect(f'/masters?entity=cm&type=i')

@login_required        
def employee_master(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    global user
    
    user = request.session.get('user_id', '')
    try:
        
        if request.method == "GET":
            id = request.GET.get('id', '')
            

            cursor.callproc("stp_get_employee_status")
            for result in cursor.stored_results():
                employee_status = list(result.fetchall())
            if id != '0':  
                id1 = decrypt_parameter(id)
                cursor.callproc("sto_get_employee_site", [id1,])    
                for result in cursor.stored_results():
                    site_name = list(result.fetchall())
            else:
                site_name = [] 
            cursor.callproc("stp_get_company_site_name",[user])
            for result in cursor.stored_results():
                company_names = list(result.fetchall())
            cursor.callproc("stp_get_dropdown_values",('states',))
            for result in cursor.stored_results():
                state_names = list(result.fetchall())
            cursor.callproc("stp_get_dropdown_values",('gender',))
            for result in cursor.stored_results():
                gender = list(result.fetchall())
            cursor.callproc("stp_get_dropdown_values",('designation',))
            for result in cursor.stored_results():
                designation_name = list(result.fetchall())
            if id == "0":
                if request.method == "GET":
                    context = {'id':id, 'employee_status':employee_status, 'employee_status_id': '','gender':gender ,'company_names':company_names,'state_names':state_names,'designation_name':designation_name}

            else:
                id1 = request.GET.get('id', '')
                id = decrypt_parameter(id1)
                cursor.callproc("stp_edit_employee_master", (id,))
                for result in cursor.stored_results():
                    data = result.fetchall()[0]  
                    context = {
                        'id':id, 
                        'employee_status':employee_status, 
                        'site_name':site_name,
                        'designation_name':designation_name,
                        'gender':gender ,
                        'company_names':company_names,
                        'state_names':state_names,
                        'employee_status':employee_status,
                        'employee_id' : data[0],
                        'employee_name': data[1],
                        'mobile_no': data[2],
                        'email':data[3], 
                        'gender_value': data[4],
                        'state_id_value':data[5],
                        'city':data[6],
                        'address':data[7],
                        'pincode':data[8],
                        'account_holder_name':data[9],
                        'account_no':data[10],
                        'bank_name':data[11],
                        'branch_name':data[12],
                        'ifsc_code':data[13],
                        'pf_no':data[14],
                        'uan_no':data[15],
                        'esic':data[16],
                        'employment_status_id': data[17],
                        'handicapped_value': data[18],
                        'is_active': data[19],     
                        'company_id_value':data[20],
                    }
                    employee_id = context['employee_id']
                    designation_list = employee_designation.objects.filter(employee_id=employee_id)
                    context['selected_designation'] = json.dumps(list(map(str, designation_list.values_list('designation_id', flat=True)))) 


                    site_list = employee_site.objects.filter(employee_id=employee_id)
                    context['selected_site'] = json.dumps(list(map(str,site_list.values_list('site_id', flat=True)))) 



        if request.method == "POST" :
            id = request.POST.get('id', '')
            if id == '0':

                employeeId = request.POST.get('employee_id', '')
                employeeName = request.POST.get('employee_name', '')
                mobile_no = request.POST.get('mobile_no', '')
                email= request.POST.get('email', '')
                gender = request.POST.get('gender', '')
                handicapped = request.POST.get('handicapped_value', '')
                address = request.POST.get('address', '')
                city = request.POST.get('city', '')
                state1 = request.POST.get('state_id', '')
                pincode = request.POST.get('pincode', '')
                company_id1 = request.POST.get('company_id', '')
                account_holder_name = request.POST.get('account_holder_name', '')
                account_no = request.POST.get('account_no', '')
                bank_name = request.POST.get('bank_name', '')
                branch_name = request.POST.get('branch_name', '')
                ifsc_code = request.POST.get('ifsc_code', '')
                pf_no = request.POST.get('pf_no', '')
                uan_no = request.POST.get('uan_no', '')
                esic = request.POST.get('esic', '')
                # employeeStatus = request.POST.get('employee_status_id', '')
                # activebtn = request.POST.get('status_value', '')
                designation_list = request.POST.getlist('designation_name', '')
                site_list = request.POST.getlist('site_name', '')
                for designation in designation_list:
                    designation_id = designation_master.objects.get(designation_id=int(designation))
                    employee_designation.objects.create(employee_id=employeeId,designation_id=designation_id)
                for site in site_list:
                    site_id = sit.objects.get(site_id=int(site))
                    employee_site.objects.create(employee_id=employeeId,site_id=site_id)

                params = [
                    employeeId, 
                    employeeName, 
                    mobile_no,
                    email, 
                    address,
                    city,
                    state1,
                    pincode,
                    company_id1,
                    account_holder_name,
                    account_no,
                    bank_name,
                    branch_name,
                    ifsc_code,
                    pf_no,
                    uan_no,
                    esic,
                    gender,
                    handicapped,
                    user
                    # employeeStatus,
                    # activebtn
                ]
                
                cursor.callproc("stp_insert_employee_master", params)
                for result in cursor.stored_results():
                        datalist = list(result.fetchall())
                if datalist[0][0] == "success":
                    messages.success(request, 'Data successfully Saved !')
                else: messages.error(request, datalist[0][0])
            else:
                id = request.POST.get('id', '')
                employee_id = request.POST.get('employee_id', '')
                employee_name = request.POST.get('employee_name', '')
                mobile_no = request.POST.get('mobile_no', '')
                email = request.POST.get('email', '')
                gender = request.POST.get('gender', '')
                handicapped = request.POST.get('handicapped_value', '')
                address = request.POST.get('address', '')
                city = request.POST.get('city', '')
                state1 = request.POST.get('state_id', '')
                pincode = request.POST.get('pincode', '')
                company_id1 = request.POST.get('company_id', '')
                account_holder_name = request.POST.get('account_holder_name', '')
                account_no = request.POST.get('account_no', '')
                bank_name = request.POST.get('bank_name', '')
                branch_name = request.POST.get('branch_name', '')
                ifsc_code = request.POST.get('ifsc_code', '')
                pf_no = request.POST.get('pf_no', '')
                uan_no = request.POST.get('uan_no', '')
                esic = request.POST.get('esic', '')
                employee_status = request.POST.get('employment_status', '')
                is_active = 1 if request.POST.get('is_active', '') == 'on' else 0 
                designation_list = request.POST.getlist('designation_name', '')
                site_list = request.POST.getlist('site_name', '')
                            
                params = [ id,employee_id, employee_name, mobile_no,email, address,city,state1,pincode,account_holder_name,account_no,bank_name,branch_name,ifsc_code,pf_no,uan_no,esic,gender,handicapped,company_id1,employee_status,is_active,user]    
                # cursor.callproc("stp_update_employee_master",params) 
                # messages.success(request, "Data successfully Updated!")

                 
                cursor.callproc("stp_update_employee_master", params)
                for result in cursor.stored_results():
                        datalist = list(result.fetchall())
               # Updating designations for the employee
                        
                employee_designation.objects.filter(employee_id=employee_id).delete()  # Replace with your actual model

                # Insert new rows with the employee_id and designation_id
                for designation_idd in designation_list:
                    # Create a new instance of the model with the employee_id and designation_id
                    designation_id1 = get_object_or_404(designation_master, designation_id=designation_idd)
                    new_entry = employee_designation(employee_id=employee_id, designation_id=designation_id1)
                    new_entry.save()

                # Deleting the existing sites for the employee
                employee_site.objects.filter(employee_id=employee_id).delete()

                # Updating sites for the employee
                for site_idd in site_list:
                    # Fetching the correct site using the 'id' field (or the correct field name)
                    site_id1 = get_object_or_404(sit, site_id=site_idd)
                    
                    # Creating a new employee-site relation
                    new_entry = employee_site(employee_id=employee_id, site_id=site_id1)
                    new_entry.save()

                
                if datalist[0][0] == "success":
                    messages.success(request, 'Data successfully Updated !')
                else: messages.error(request, datalist[0][0])

    except Exception as e:
        print(f"Error: {e}")  # Temporary for debugging
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), user])  
        messages.error(request, 'Oops...! Something went wrong!')


    
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method=="GET":
            return render(request, "Master/master/employee_master.html", context)
        elif request.method=="POST":  
            return redirect(f'/masters?entity=em&type=i')
        
@login_required  
def upload_excel(request):

    if request.method == 'POST' and request.FILES.get('excelFile'):
        excel_file = request.FILES['excelFile']
        file_name = excel_file.name
        df = pd.read_excel(excel_file)
        total_rows = len(df)
        update_count = error_count = success_count = 0
        checksum_id = None
        r=None
        global user
        user  = request.session.get('user_id', '')
        try:
            Db.closeConnection()
            m = Db.get_connection()
            cursor = m.cursor()
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
            company_id1 = request.POST.get('company_id', None)
            cursor.callproc("stp_get_masters", [entity, type, 'sample_xlsx',user])
            for result in cursor.stored_results():
                columns = [col[0] for col in result.fetchall()]
            if not all(col in df.columns for col in columns):
                messages.error(request, 'Oops...! The uploaded Excel file does not contain the required columns.!')
                return redirect(f'/masters?entity={entity}&type={type}')
            upload_for = {'em': 'employee master','sm': 'site master','cm': 'company master','r': 'roster'}[entity]
            cursor.callproc('stp_insert_checksum', (upload_for,company_id1,str(datetime.now().month),str(datetime.now().year),file_name))
            for result in cursor.stored_results():
                c = list(result.fetchall())
            checksum_id = c[0][0]

            if entity == 'em':
                success_count = 0
                error_count = 0
                update_count = 0
                for index, row in df.iterrows():
                    row_error_found = False
                    row_was_updated = False
                    # Retrieve employee_id from the current row
                    employee_id1 = row['Employee Id']  # Ensure this matches your DataFrame's column name

                    row_filtered = row.drop(['worksite', 'designation'], errors='ignore')
                    params = tuple(str(row_filtered.get(column, '')) for column in columns if column not in ['worksite', 'designation'])
                    
                    # After validation, add company_id to params
                    params += (str(company_id1),)
                    params += (str(user),)
                    merged_list = list(zip(columns, params))

                    print(merged_list)

                    # Loop through each (column, value) pair in the merged_list for custom validation
                    for column, value in merged_list:
                        # Convert value to string and lowercase, then print for debugging
                        if isinstance(value, str):
                            value = value.strip().lower()

                        # Skip validation and error logging for 'Designation' and 'Worksite' columns
                        if column in ['Designation', 'Worksite']:
                            continue  # Skip to the next iteration if the column is 'designation' or 'worksite'

                        # Call the stored procedure with employee_id1
                        cursor.callproc('stp_employee_validation', [column, value, employee_id1])
                        for result in cursor.stored_results():
                            r = list(result.fetchall())
                            if r and r[0][0] not in ("", None, " ", "Success"):
                                error_message = str(r[0][0])
                                # Ensure proper logging for errors
                                cursor.callproc('stp_insert_error_log', [upload_for, company_id1, file_name, datetime.now().date(), error_message, checksum_id, employee_id1])
                                error_count += 1
                                row_error_found = True 

                    if not row_error_found:

                        employee_exists = sc_employee_master.objects.filter(employee_id=employee_id1).exists()
                        # Check if the row is an update or a new insert

                        if employee_exists:
                            cursor.callproc('stp_update_employee_master_excel', params)
                            for result in cursor.stored_results():
                                update_result = result.fetchone()
                        else:
                            cursor.callproc('stp_employeeinsertexcel', params)
                            for result in cursor.stored_results():
                                update_result = result.fetchone()

                        
                            if update_result == "Updated":
                                update_count += 1  
                                row_was_updated = True
                            elif update_result == "Success":
                                success_count += 1  

                
                df.columns = df.columns.str.strip()  


                if 'Employee Id' in df.columns and 'Designation' in df.columns:
                    # print("Both 'employee id' and 'designation' found in DataFrame.")

                   
                    df_designations = df[['Employee Id', 'Designation']].dropna(subset=['Designation']).copy()
                    df_designations['company_id'] = company_id1  
                    
                    for index, row in df_designations.iterrows():
                        employee_id = row['Employee Id']
                        designations = row['Designation'].split(',')  

                       
                        for designation in designations:
                            designation = designation.strip()  
                            
                            
                            cursor.callproc('stp_insert_employee_designation', [employee_id, designation, company_id1])

                          
                            for result in cursor.stored_results():
                                r = list(result.fetchall())

                            if r:
                                result_value = r[0][0]  

                                if result_value == "success":
                                    success_count += 1
                                elif result_value == "updated":
                                    update_count += 1
                                elif result_value.startswith("error"):
                                    # Log the error message in your error log table
                                    error_message = result_value  # The error message from the procedure
                                    cursor.callproc('stp_insert_error_log', [
                                        upload_for, company_id1, file_name, datetime.now().date(), error_message, checksum_id,employee_id
                                    ])
                                    error_count += 1  # Increment error count for errors

                else:
                    # In case 'employee id' or 'designation' is missing in df.columns
                    print("Required columns 'employee id' or 'designation' not found in the DataFrame.")

                       #   this is for worksite insert  
                if 'Employee Id' in df.columns and 'Worksite' in df.columns:
                    # print("Both 'employee id' and 'worksite' found in DataFrame.")

                    # Create a second DataFrame for 'employee_id', 'designation', and company_id
                    df_worksite = df[['Employee Id', 'Worksite']].dropna(subset=['Worksite']).copy()
                    df_worksite['company_id'] = company_id1  # Add company_id to df_designations

                    # Loop through each row in the DataFrame
                    for index, row in df_worksite.iterrows():
                        employee_id = row['Employee Id']
                        worksite = row['Worksite'].split(',')  # Assuming multiple designations are comma-separated

                        # Loop through each designation and insert it into the employee_designation table
                        for worksite in worksite:
                            worksite = worksite.strip()  # Trim spaces from the designation
                            
                            # Call the stored procedure to insert the designation for the employee
                            cursor.callproc('stp_insert_employee_site', [employee_id, worksite, company_id1])

                            # Fetch all stored results to check the response from the procedure
                            for result in cursor.stored_results():
                                r = list(result.fetchall())

                            if r:
                                result_value = r[0][0]  # Fetch the result from the stored procedure

                                if result_value == "success":
                                    success_count += 1
                                elif result_value == "updated":
                                    update_count += 1
                                elif result_value.startswith("error"):
                                    # Log the error message in your error log table
                                    error_message = result_value  # The error message from the procedure
                                    cursor.callproc('stp_insert_error_log', [
                                        upload_for, company_id1, file_name, datetime.now().date(), error_message, checksum_id,employee_id1
                                    ])
                                    error_count += 1  # Increment error count for errors

                else:
                    # In case 'employee id' or 'designation' is missing in df.columns
                    print("Required columns 'employee id' or 'worksite' not found in the DataFrame.")
            elif entity == 'sm':
                for index, row in df.iterrows():
                    state_name = str(row.get('State', ''))
                    city_name = str(row.get('City', ''))
                    
                    try:
                        state_obj = StateMaster.objects.get(state_name=state_name)
                        state_id = state_obj.state_id
                    except StateMaster.DoesNotExist:
                        state_id = None  # State not found
                    
                    try:
                        city_obj = CityMaster.objects.get(city_name=city_name)
                        city_id = city_obj.city_id
                    except CityMaster.DoesNotExist:
                        city_id = None  # City not found

                    # Check if state_id or city_id is None and log error
                    if state_id is None:
                        error_message = f"Please provide a Valid State for the Worksite '{row.get('Site Name')}' at row number {index + 1}"
                        cursor.callproc('stp_site_error_log', [upload_for, company_id1, file_name, datetime.now().date(), error_message, checksum_id, ''])
                    
                    if city_id is None:
                        error_message = f"Please provide a Valid City for the Worksite '{row.get('Site Name')}' at row number {index + 1}"
                        cursor.callproc('stp_site_error_log', [upload_for, company_id1, file_name, datetime.now().date(), error_message, checksum_id, ''])

                    # Only proceed to insert into site_master if state_id and city_id are not None
                    if state_id is not None and city_id is not None:
                        # Get the other parameters
                        params = tuple(str(row.get(column, '')) for column in columns if column not in ['State', 'City'])
                        params += (str(state_id), str(city_id))
                        params += (str(company_id1),)
                        params += (str(user),)

                        # Insert data into the site_master table
                        cursor.callproc('stp_insert_site_master_excel', params)
                        
                        # Check the result from the stored procedure
                        for result in cursor.stored_results():
                            r = list(result.fetchall())

                        if r[0][0] not in ("success", "updated"):
                            # Log error if the result is not success or updated
                            cursor.callproc('stp_site_error_log', [upload_for, company_id1, file_name, datetime.now().date(), str(r[0][0]), checksum_id, str(row.get('Site Name'))])

                    
                    # Increment counters based on the result
                    if r[0][0] == "success":
                        success_count += 1
                    elif r[0][0] == "updated":
                        update_count += 1
                    else:
                        error_count += 1
            elif entity == 'cm':
                for index,row in df.iterrows():
                    params = tuple(str(row.get(column, '')) for column in columns)
                    cursor.callproc('stp_insert_company_master', params)
                    for result in cursor.stored_results():
                            r = list(result.fetchall())
                    if r[0][0] not in ("success", "updated"):
                        cursor.callproc('stp_insert_error_log', [upload_for, company_id1,'',file_name,datetime.now().date(),str(r[0][0]),checksum_id])
                    if r[0][0] == "success": success_count += 1 
                    elif r[0][0] == "updated": update_count += 1  
                    else: error_count += 1
            checksum_msg = f"Total Rows Processed: {total_rows}, Successful Entries: {success_count}" f"{f', Updates: {update_count}' if update_count > 0 else ''}" f"{f', Errors: {error_count}' if error_count > 0 else ''}"
            cursor.callproc('stp_update_checksum', (upload_for,company_id1,'',str(datetime.now().month),str(datetime.now().year),file_name,checksum_msg,error_count,update_count,checksum_id,''))
            if error_count == 0 and update_count == 0 and success_count > 0:
                messages.success(request, f"All data uploaded successfully!.")
            elif error_count == 0 and success_count == 0 and update_count > 0:
                messages.success(request, f"All data updated successfully!.")
            else:messages.warning(request, f"The upload processed {total_rows} rows, resulting in {success_count} successful entries"  f"{f', {update_count} updates' if update_count > 0 else ''}" f", and {error_count} errors; please check the error logs for details.")
                   
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            cursor.callproc("stp_error_log", [fun, str(e), user])  
            messages.error(request, 'Oops...! Something went wrong!')
            m.commit()   
        finally:
            cursor.close()
            m.close()
            Db.closeConnection()
            return redirect(f'/masters?entity={entity}&type=i')
        
def view_employee(request):
    Db.closeConnection()  
    m = Db.get_connection()
    cursor = m.cursor()
    try:
        if request.method == "GET":
            id = request.GET.get('id', '')

            # Initialize context variable before starting to populate it
            context = {
                'id': id,
                'employee_status': [],
                'employee_status_id': '',
                'site_name': [],
                'gender': [],
                'company_names': [],
                'state_names': [],
                'designation_name': [],
                'employee_id': None,
                'employee_name': None,
                'mobile_no': None,
                'email': None,
                'gender_value': None,
                'state_id_value': None,
                'city': None,
                'address': None,
                'pincode': None,
                'account_holder_name': None,
                'account_no': None,
                'bank_name': None,
                'branch_name': None,
                'ifsc_code': None,
                'pf_no': None,
                'uan_no': None,
                'esic': None,
                'employment_status_id': None,
                'handicapped_value': None,
                'is_active': None,
                'company_id_value': None,
                'selected_designation': [],
                'selected_site': []
            }

            # Populate dropdown values
            cursor.callproc("stp_get_employee_status")
            for result in cursor.stored_results():
                context['employee_status'] = list(result.fetchall())

            cursor.callproc("stp_get_dropdown_values", ('site',))
            for result in cursor.stored_results():
                context['site_name'] = list(result.fetchall())

            cursor.callproc("stp_get_dropdown_values", ('company',))
            for result in cursor.stored_results():
                context['company_names'] = list(result.fetchall())

            cursor.callproc("stp_get_dropdown_values", ('states',))
            for result in cursor.stored_results():
                context['state_names'] = list(result.fetchall())

            cursor.callproc("stp_get_dropdown_values", ('gender',))
            for result in cursor.stored_results():
                context['gender'] = list(result.fetchall())

            cursor.callproc("stp_get_dropdown_values", ('designation',))
            for result in cursor.stored_results():
                context['designation_name'] = list(result.fetchall())

           

            # Otherwise, we are editing an existing employee
            id1 = request.GET.get('id', '')
            id = decrypt_parameter(id1)

            cursor.callproc("stp_edit_employee_master", (id,))
            for result in cursor.stored_results():
                data = result.fetchall()[0]
                context.update({
                    'employee_id': data[0],
                    'employee_name': data[1],
                    'mobile_no': data[2],
                    'email': data[3],
                    'gender_value': data[4],
                    'state_id_value': data[5],
                    'city': data[6],
                    'address': data[7],
                    'pincode': data[8],
                    'account_holder_name': data[9],
                    'account_no': data[10],
                    'bank_name': data[11],
                    'branch_name': data[12],
                    'ifsc_code': data[13],
                    'pf_no': data[14],
                    'uan_no': data[15],
                    'esic': data[16],
                    'employment_status_id': data[17],
                    'handicapped_value': data[18],
                    'is_active': data[19],
                    'company_id_value': data[20],
                })

                # Get the employee's designation and site info
                employee_id = context['employee_id']
                designation_list = employee_designation.objects.filter(employee_id=employee_id)
                context['selected_designation'] = json.dumps(list(map(str, designation_list.values_list('designation_id', flat=True))))

                site_list = employee_site.objects.filter(employee_id=employee_id)
                context['selected_site'] = json.dumps(list(map(str, site_list.values_list('site_id', flat=True))))

    except Exception as e:
        print(f"Error: {e}")  # Temporary for debugging
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), user])  
        messages.error(request, 'Oops...! Something went wrong!')

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()

        if request.method == "GET":
            return render(request, "Master/master/employee_view.html", context)
        elif request.method == "POST":  
            return redirect(f'/masters?entity=em&type=i')
        
@login_required        
def designation_master1(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    global user
    
    # user_id = request.session.get('user_id', '')
    # user = CustomUser.objects.get(id=user_id)
    try:
        
        if request.method == "GET":
           
            designation_id = request.GET.get('designation_id', '')
            if designation_id == "0":
                if request.method == "GET":
                    context = {'designation_id':designation_id}

            else:
                designation_id = request.GET.get('designation_id', '')
                designation_id = decrypt_parameter(designation_id)
                cursor.callproc("stp_designationedit", (designation_id,))
                for result in cursor.stored_results():
                    data = result.fetchall()[0]  
                    context = {
                        'designation_id': data[0],
                        'designation_name': data[1],
                        'is_active':data[2]
                    }

        if request.method == "POST" :
            id = request.POST.get('designation_id', '')
            if id == '0':
                designation_name = request.POST.get('designation_name', '')
                # is_active = request.POST.get('is_active', '') 
                params = [
                    designation_name,
                    # is_active  
                ]
                cursor.callproc("stp_designationinsert", params)
                for result in cursor.stored_results():
                        datalist = list(result.fetchall())
                if datalist[0][0] == "success":
                    messages.success(request, 'Data successfully entered !')
                else: messages.error(request, datalist[0][0])
            else:
                designation_id = request.POST.get('designation_id', '')
                designation_name = request.POST.get('designation_name', '')
                # is_active1 = request.POST.get('is_active', '')
                is_active = 1 if request.POST.get('is_active') == 'on' else 0 
                            
                params = [designation_id,designation_name,is_active]    
                cursor.callproc("stp_designationupdate",params) 
                messages.success(request, "Data successfully Updated!")

    except Exception as e:
        print(f"Error: {e}")  # Temporary for debugging
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), user])  
        messages.error(request, 'Oops...! Something went wrong!')

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()

        if request.method == "GET":
            return render(request, "Master/master/designation_master.html", context)
        elif request.method == "POST":  
            return redirect(f'/masters?entity=dm&type=i')

def view_designation(request):
    Db.closeConnection()  
    m = Db.get_connection()
    cursor = m.cursor()
    try:
        if request.method == "GET":
            designation_id = request.GET.get('designation_id', '')

            # Initialize context variable before starting to populate it
            context = {
                'designation_id': None,
                'designation_name': None,
                'is_active': None
            }

            # Otherwise, we are editing an existing employee
            designation_id1 = request.GET.get('designation_id', '')
            designation_id = decrypt_parameter(designation_id1)

            cursor.callproc("stp_designationedit", (designation_id,))
            for result in cursor.stored_results():
                data = result.fetchall()[0]
                context.update({
                    'designation_id': data[0],
                    'designation_name': data[1],
                    'is_active': data[2],
                })


    except Exception as e:
        print(f"Error: {e}")  # Temporary for debugging
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), user])  
        messages.error(request, 'Oops...! Something went wrong!')

    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()

        if request.method == "GET":
            return render(request, "Master/master/designation_view.html", context)
        elif request.method == "POST":  
            return redirect(f'/masters?entity=dm&type=i')

@login_required
def employee_upload(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    pre_url = request.META.get('HTTP_REFERER')
    header, data = [], []
    entity, type, name = '', '', ''
    global user
    user  = request.session.get('user_id', '')
    try:
         
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
            
            cursor.callproc("stp_get_company_site_name",[user])
            for result in cursor.stored_results():
                site_name = list(result.fetchall())
            cursor.callproc("stp_get_dropdown_values",['designation'])
            for result in cursor.stored_results():
                designation_name = list(result.fetchall())
            cursor.callproc("stp_get_assigned_company",[user])
            for result in cursor.stored_results():
                company_names = list(result.fetchall())
            cursor.callproc("stp_get_dropdown_values",['states'])
            for result in cursor.stored_results():
                state_name = []
                state_name = list(result.fetchall())
                

        if request.method=="POST":
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
            if entity == 'r' and type == 'ed':
                ids = request.POST.getlist('ids[]', '')
                shifts = request.POST.getlist('shifts[]', '')
                for id,shift in zip(ids, shifts):
                    cursor.callproc("stp_post_roster",[id,shift])
                    for result in cursor.stored_results():
                        datalist = list(result.fetchall())
                if datalist[0][0] == "success":
                    messages.success(request, 'Data updated successfully !')
            if entity == 'urm' and (type == 'acu' or type == 'acr'):
                
                created_by = request.session.get('user_id', '')
                ur = request.POST.get('ur', '')
                selected_company_ids = list(map(int, request.POST.getlist('company_id')))
                selected_worksites  = request.POST.getlist('worksite')
                company_worksite_map = {}
                
                if not selected_company_ids or not selected_worksites:
                    messages.error(request, 'Company or worksite data is missing!')
                    return redirect(f'/masters?entity={entity}&type=urm')
                if type not in ['acu', 'acr'] or not ur:
                    messages.error(request, 'Invalid data received.')
                    return redirect(f'/masters?entity={entity}&type=urm')
                
                cursor.callproc("stp_get_company_worksite",[",".join(request.POST.getlist('company_id'))])
                for result in cursor.stored_results():
                    company_worksites  = list(result.fetchall())
                    
                for company_id, worksite_name in company_worksites:
                    if company_id not in company_worksite_map:
                        company_worksite_map[company_id] = []
                    company_worksite_map[company_id].append(worksite_name)
                
                filtered_combinations = []
                for company_id in selected_company_ids:
                    valid_worksites = company_worksite_map.get(company_id, [])
                    # Filter worksites that were actually selected by the user
                    selected_valid_worksites = [ws for ws in selected_worksites if ws in valid_worksites]
                    filtered_combinations.extend([(company_id, ws) for ws in selected_valid_worksites])
                    
                cursor.callproc("stp_delete_access_control",[type,ur])
                r=''
                for company_id, worksite in filtered_combinations:
                    cursor.callproc("stp_post_access_control",[type,ur,company_id,worksite,created_by])
                    for result in cursor.stored_results():
                            r = list(result.fetchall())
                type='urm'
                if r[0][0] == "success":
                    messages.success(request, 'Data updated successfully !')
                
            else : messages.error(request, 'Oops...! Something went wrong!')
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method=="GET":
            return render(request,'Master/employee_upload.html', {'entity':entity,'type':type,'name':name,'company_names':company_names,'state_name':state_name,'site_name':site_name,'designation_name':designation_name,'pre_url':pre_url})
        elif request.method=="POST":  
            new_url = f'/masters1?entity={entity}&type={type}'
            return redirect(new_url)      

@login_required
def worksite_upload(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    pre_url = request.META.get('HTTP_REFERER')
    header, data = [], []
    entity, type, name = '', '', ''
    global user
    user  = request.session.get('user_id', '')
    try:
         
        if request.method=="GET":
            entity = request.GET.get('entity', '')
            type = request.GET.get('type', '')
            
            cursor.callproc("stp_get_userwise_dropdown",[user,'company'])
            for result in cursor.stored_results():
                company_names = list(result.fetchall())
                  # Fetching combined city and state data using stp_city_state
            cursor.callproc("stp_city_state")
            for result in cursor.stored_results():
                city_state_data = list(result.fetchall())
                
    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method=="GET":
            return render(request,'Master/worksite_upload.html', {'entity':entity,'type':type,'name':name,'header':header,'company_names':company_names,'city_state_data':city_state_data,'data':data,'pre_url':pre_url})
        elif request.method=="POST":  
            new_url = f'/masters1?entity={entity}&type={type}'
            return redirect(new_url)  
        
def upload_excel_cm(request):

    if request.method == 'POST' and request.FILES.get('excelFile'):
        excel_file = request.FILES['excelFile']
        file_name = excel_file.name
        df = pd.read_excel(excel_file)
        total_rows = len(df)
        update_count = error_count = success_count = 0
        checksum_id = None
        r=None
        global user
        user  = request.session.get('user_id', '')
        try:
            Db.closeConnection()
            m = Db.get_connection()
            cursor = m.cursor()
            entity = request.POST.get('entity', '')
            type = request.POST.get('type', '')
            company_id1 = request.POST.get('company_id', None)
            cursor.callproc("stp_get_masters", [entity, type, 'sample_xlsx',user])
            for result in cursor.stored_results():
                columns = [col[0] for col in result.fetchall()]
            if not all(col in df.columns for col in columns):
                messages.error(request, 'Oops...! The uploaded Excel file does not contain the required columns.!')
                return redirect(f'/masters?entity={entity}&type={type}')
            upload_for = {'em': 'employee master','sm': 'site master','cm': 'company master','r': 'roster'}[entity]
            cursor.callproc('stp_insert_checksum', (upload_for,company_id1,str(datetime.now().month),str(datetime.now().year),file_name))
            for result in cursor.stored_results():
                c = list(result.fetchall())
            checksum_id = c[0][0]

            for index,row in df.iterrows():
                params = tuple(str(row.get(column, '')) for column in columns)
                cursor.callproc('stp_insert_company_master', params)
                for result in cursor.stored_results():
                    r = list(result.fetchall())
                if r[0][0] not in ("success", "updated"):
                    cursor.callproc('stp_insert_error_log_cm', [upload_for,company_id1,file_name,datetime.now().date(),str(r[0][0]),checksum_id,])
                if r[0][0] == "success": success_count += 1 
                elif r[0][0] == "updated": update_count += 1  
                else: error_count += 1
            checksum_msg = f"Total Rows Processed: {total_rows}, Successful Entries: {success_count}" f"{f', Updates: {update_count}' if update_count > 0 else ''}" f"{f', Errors: {error_count}' if error_count > 0 else ''}"
            cursor.callproc('stp_update_checksum', (upload_for,company_id1,'',str(datetime.now().month),str(datetime.now().year),file_name,checksum_msg,error_count,update_count,checksum_id))
            if error_count == 0 and update_count == 0 and success_count > 0:
                messages.success(request, f"All data uploaded successfully!.")
            elif error_count == 0 and success_count == 0 and update_count > 0:
                messages.warning(request, f"All data updated successfully!.")
            else:messages.warning(request, f"The upload processed {total_rows} rows, resulting in {success_count} successful entries"  f"{f', {update_count} updates' if update_count > 0 else ''}" f", and {error_count} errors; please check the error logs for details.")
                   
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            cursor.callproc("stp_error_log", [fun, str(e), user])  
            messages.error(request, 'Oops...! Something went wrong!')
            m.commit()   
        finally:
            cursor.close()
            m.close()
            Db.closeConnection()
            return redirect(f'/masters?entity={entity}&type=i')
        
def site_master(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    global user
    user  = request.session.get('user_id', '')
    try:
        
        if request.method == "GET":
            # cursor.callproc("stp_get_roster_type")
            # for result in cursor.stored_results():
            #     roster_types = list(result.fetchall())
                # Call stored procedure to get company names
            cursor.callproc("stp_get_userwise_dropdown", [user,'company'])
            for result in cursor.stored_results():
                company_names = list(result.fetchall())
            cursor.callproc("stp_get_state_names")
            for result in cursor.stored_results():
                state_names = list(result.fetchall())
            cursor.callproc("stp_get_city_names")
            for result in cursor.stored_results():
                city_names = list(result.fetchall())
                
            site_id = request.GET.get('id', '')
            # site_id = decrypt_parameter(str(site_id))
            if site_id == "0":
                if request.method == "GET":
                    context = {'company_names': company_names, 'state_names': state_names,'site_id':site_id}

            else:
                # site_id1 = request.GET.get('site_id', '')
                # site_id = decrypt_parameter(site_id1)

                # cursor.callproc("stp_edit_site_master",(site_id, )) 
                # for result in cursor.stored_results():
                #     data = result.fetchall()[0]
                site_id1 = request.GET.get('site_id', '')
                site_id = decrypt_parameter(site_id1)
                cursor.callproc("stp_edit_site_master", (site_id,)) 
                for result in cursor.stored_results():
                    data = result.fetchall()[0] 

                    context = {
                        'company_names': company_names,
                        'state_names': state_names,
                        'city_names': city_names,
                        'site_id': site_id[0],
                        'site_name': data[1],
                        'site_address': data[2],
                        'pincode': data[3],
                        'state_id': data[4],
                        'contact_person_name': data[5],
                        'contact_person_email': data[6],
                        'contact_person_mobile_no': data[7],
                        'is_active': data[8],
                        'company_name': data[9],
                        'city': data[10],
                    }
                
            
        if request.method == "POST":
            siteId = request.POST.get('site_id', '')
            if siteId == "0":
                # response_data = {"status": "fail"}
                try:
                    siteName = request.POST.get('siteName', '')
                    siteAddress = request.POST.get('siteAddress', '')
                    pincode = request.POST.get('pincode', '')
                    contactPersonName = request.POST.get('contactPersonName', '')
                    contactPersonEmail = request.POST.get('contactPersonEmail', '')
                    contactPersonMobileNo = request.POST.get('Number', '')  
                    # is_active = request.POST.get('status_value', '') 
                    # noOfDays = request.POST.get('FieldDays', '')  
                    # notificationTime = request.POST.get('notificationTime', '')
                    # ReminderTime = request.POST.get('ReminderTime', '')
                    companyId = request.POST.get('company_id', '')  
                    stateId = request.POST.get('state_id', '')  
                    cityId = request.POST.get('city_id', '')  
                    # rosterType = request.POST.get('roster_type', '')
                
                    params = [
                        siteName, 
                        siteAddress, 
                        pincode, 
                        contactPersonName, 
                        contactPersonEmail, 
                        contactPersonMobileNo, 
                        # is_active,
                        # noOfDays, 
                        # notificationTime, 
                        # ReminderTime,
                        stateId,
                        cityId,
                        companyId,
                        user
                        # rosterType
                    ]
                    
                    cursor.callproc("stp_insert_site_master", params)
                    for result in cursor.stored_results():
                            datalist = list(result.fetchall())
                    if datalist[0][0] == "success":
                        messages.success(request, 'Data successfully entered !')
                    else: messages.error(request, datalist[0][0])
                except Exception as e:
                    tb = traceback.extract_tb(e.__traceback__)
                    fun = tb[0].name
                    cursor.callproc("stp_error_log", [fun, str(e), user])  
                    messages.error(request, 'Oops...! Something went wrong!')
            else:
                if request.method == "POST" :
                    siteId = request.POST.get('site_id', '')
                    siteName = request.POST.get('siteName', '')
                    siteAddress = request.POST.get('siteAddress', '')
                    pincode = request.POST.get('pincode', '')
                    contactPersonName = request.POST.get('contactPersonName', '')
                    contactPersonEmail = request.POST.get('contactPersonEmail', '')
                    contactPersonMobileNo = request.POST.get('Number', '')  
                    # noOfDays = request.POST.get('FieldDays', '') 
                    isActive = request.POST.get('status_value', '')
                    # notificationTime = request.POST.get('notificationTime', '')
                    # ReminderTime = request.POST.get('ReminderTime', '')
                    companyId = request.POST.get('company_id', '')  
                    stateId = request.POST.get('state_id', '')  
                    cityId = request.POST.get('city_id', '')  
                    # Rostertype = request.POST.get('roster_type', '')
                    
                    params = [siteId,siteName,siteAddress,pincode,contactPersonName,contactPersonEmail,
                                        contactPersonMobileNo,isActive,companyId,stateId,cityId,user]
                    cursor.callproc("stp_update_site_master",params) 
                    messages.success(request, "Data updated successfully...!")

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), user])  
        messages.error(request, 'Oops...! Something went wrong!')
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
            
        if request.method=="GET":
            return render(request, "Master/master/site_master.html", context)
        elif request.method=="POST":  
            return redirect( f'/masters?entity=sm&type=i')

def get_worksites(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    
    try:
        user_id = request.session.get('user_id', '')
        selectedCompany = request.POST.get('selectedCompany','')
        cursor.callproc("stp_get_slot_siteName", [user_id,selectedCompany])
        for result in cursor.stored_results():
            companywise_site_names = list(result.fetchall())

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log", [fun, str(e), request.user.id])
        print(f"error: {e}")
        return JsonResponse({'result': 'fail', 'message': 'something went wrong!'}, status=500)
    
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
    
    return JsonResponse({'companywise_site_names': companywise_site_names}, status=200)

def fetch_cities(request):
    try:
        if request.method == "GET":
            state_id = request.GET.get('state_id')
            # Query city names based on the state_id
            city_names = CityMaster.objects.filter(state_id=state_id).values_list('city_id', 'city_name')
            return JsonResponse({'city_names': list(city_names)})
    except Exception as e:
        # Log the exception using your stored procedure
        print(e)
@csrf_exempt
def get_access_control(request):
    Db.closeConnection()
    m = Db.get_connection()
    global user
    user  = request.session.get('user_id', '')
    try:
        if request.method == "POST":
            type1 = request.POST.get('type1','')
            type = request.POST.get('type','')
            ur = request.POST.get('ur', '')
            company = callproc("stp_get_access_control_val", [type,ur,'company'])
            worksite = callproc("stp_get_access_control_val", [type,ur,'worksite'])
            if type1 == 'worksites':
                company_id = request.POST.getlist('company_id','')
                company_ids = ','.join(company_id)
                worksite = callproc("stp_get_access_control_val", [type1,company_ids,'worksites'])
                response = {
                    'result': 'success',
                    'worksite':worksite,
                    'company': company,
                    'worksite': worksite,
                }
            else:     
                response = {
                    'result': 'success',
                    'worksite':worksite,
                    'company': company,
                }

        # Return JSON response
            return JsonResponse(response)
        else: response = {'result': 'fail', 'message': 'Invalid request method'}

    except Exception as e:
        tb = traceback.extract_tb(e.__traceback__)
        callproc("stp_error_log", [tb[0].name, str(e), user])
        print(f"error: {e}")
        response = {'result': 'fail', 'message': 'Something went wrong!'}

    finally:
        m.close()
        Db.closeConnection()
        return JsonResponse(response)