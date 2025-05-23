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

from Test.models import *
import random
from random import shuffle
from THRMS.encryption import enc, dec
from django.utils.timezone import now
from django.db.models import OuterRef, Subquery

@login_required
def enterthedetails(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    
    try:
        user = request.user.id 
        if request.method == "GET":
            ErrorMessage =request.GET.get('ErrorMessage', '')
            SuccessMessage =request.GET.get('SuccessMessage', '')            
            dpl = PostMaster.objects.values_list('id', 'post')
        if request.method == "POST":
            name1 = request.POST.get("text_name", "")
            email1 = request.POST.get("email", "")
            mobile1 = request.POST.get("mobile", "")
            post1 = request.POST.get("post", "")                                              
            noq1 = request.POST.get("noq", "")
            noq = int(noq1)
            # Get and shuffle questions
            all_questions = list(QuestionAnswerMaster.objects.filter(post=post1))
            if not all_questions:
                questions_var = "no_questions"
            else:
                questions_var = "questions_exist" 
                
            if all_questions:                
                shuffle(all_questions)
                selected_questions = all_questions[:min(noq, len(all_questions))]

                # Extract question IDs
                question_ids = [str(q.question_id) for q in selected_questions]
                ids_str1 = ",".join(question_ids)
                ids_str = enc(str(ids_str1))

                # exists = CandidateTestMaster.objects.filter(name=name1, mobile=mobile1).exists()
                # if not exists:
                CandidateTestMaster.objects.create(
                    name=name1,
                    email=email1,
                    mobile=mobile1,
                    post=post1,
                    created_at=timezone.now(),
                    created_by=user
                )  
                    
                candidate_id2 = CandidateTestMaster.objects.filter(name=name1, mobile=mobile1).values_list('id', flat=True).first()
                candidate_id = enc(str(candidate_id2))                
                                                                
    except Exception as e:
        print("error-" + e)
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),request.user.id])          
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method == "GET":
            return render(request, "Test/enter_details.html", {'dpl': dpl})
        elif request.method == "POST":
            if questions_var == "no_questions":
                messages.error(request,"No Questions Found For This Post !!!!") 
                return redirect('enterthedetails')
            else:                
                return redirect(f'/test_page?zparqwwq={ids_str}&candidate_id={candidate_id}')                    
        
@login_required
def test_page(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    
    try:
        user = request.user.id 
        if request.method == "GET":
            start_time1 = timezone.now()
            start_time = enc(str(start_time1))
            candidate_id1 = request.GET.get("candidate_id", "")
            # candidate_id=dec(candidate_id1)
            ids_str1 = request.GET.get("zparqwwq", "") #this are question ids 
            ids_str=dec(ids_str1)
            id_list = [int(qid) for qid in ids_str.split(",") if qid.isdigit()]  
            
            questions = QuestionAnswerMaster.objects.filter(question_id__in=id_list)
            questions = sorted(questions, key=lambda q: id_list.index(q.question_id))                     

        if request.method == "POST":

            question_ids = request.POST.getlist("question_ids")
            candidate_id1 = request.POST.get("candidate_id", "")
            candidate_id=dec(candidate_id1)
                         
            start_time1 = request.POST.get("start_time", "")
            start_time_str=dec(start_time1)             

            
# GET CANDIDATE DETAILS            
            candidate_data = CandidateTestMaster.objects.filter(id=candidate_id).values('name', 'post').first()
            candidate_name = candidate_data['name']
            post1 = candidate_data['post']
            start_time = enc(str(start_time1))


# TIME TAKEN BY CANDIDATE
            
            start_time = datetime.fromisoformat(start_time_str)
            end_time = now()
            time_taken = end_time - start_time
            # Convert to minutes and seconds
            seconds_taken = int(time_taken.total_seconds())
            hours = seconds_taken // 3600
            minutes = (seconds_taken % 3600) // 60
            seconds = seconds_taken % 60

            # Optional: format as string "mm:ss"
            time_taken_str = f"{hours:02}:{minutes:02}:{seconds:02}"  # HH:MM:SS           

# SCORE CALCULATION OF CANDIDATE 
            score = 0
            total = len(question_ids)
            result_details = []            
            for qid in question_ids:
                question = QuestionAnswerMaster.objects.get(pk=int(qid))
                user_answer = request.POST.get(f"answer_{qid}", "")
                is_correct = (user_answer == question.correct_answer) 

                if is_correct:
                    isright1 = "Yes"
                    score += 1 
                else:
                    isright1 = "No"     
                    
                candidate_answer = CandidateAnswer(
                    candidate_id=candidate_id,
                    post=post1,
                    question_id=qid,
                    candidates_answer=user_answer,
                    is_right=isright1,
                    created_at=timezone.now(),
                    created_by=user
                )

                candidate_answer.save()
                
# PERCENTAGE CALCULATION & STATUS
            percentage = (score / total) * 100 
            if percentage >= 40:
                status = "pass"
            else:
                status = "fail"   
                
            CandidateTestMaster.objects.filter(id=candidate_id).update(
                marks_received=score,
                out_of=total,
                time_taken=time_taken_str,
                percentage=percentage,
                status=status,
                updated_by=user,
                updated_at=timezone.now(),
                test_start_time=start_time,
                test_end_time=end_time
            )                                                                                                       
            
    except Exception as e:
        print("error-" + e)
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),request.user.id])          
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method == "GET":
            return render(request, "Test/test_page.html",{"questions": questions,"candidate_id":candidate_id1,"start_time":start_time})
        elif request.method == "POST":
            return redirect(f'/result_page?cname={candidate_id1}')     
        
@login_required
def result_page(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    
    try:
        if request.method == "GET":                                    
            candidate_id1 = request.GET.get("cname", "") 
            candidate_id=dec(candidate_id1)       
            # Fetch the candidate record by ID and get specific fields
            candidate = CandidateTestMaster.objects.filter(id=candidate_id).values('name', 'time_taken', 'percentage', 'status').first()

            # Initialize variables to None in case no record is found
            name = time_taken = percentage = status = None

            # If candidate record exists, extract fields into separate variables
            if candidate:
                name = candidate['name']
                time_taken = candidate['time_taken']
                percentage = candidate['percentage']
                status = candidate['status']                 
    except Exception as e:
        print("error-" + e)
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),request.user.id])          
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method == "GET":
            return render(request, "Test/result_page.html",{"candidate_name":name,"time_taken":time_taken,"percentage":percentage,"status":status})
        
@login_required
def test_index(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor = m.cursor()
    
    try:
        if request.method == "GET": 
            
            # Subquery to fetch post name from PostMaster
            post_name_subquery = PostMaster.objects.filter(
                id=OuterRef('post')  # both are IntegerFields now
            ).values('post')[:1]

            # Annotate queryset with post name
            queryset = CandidateTestMaster.objects.annotate(
                post_name=Subquery(post_name_subquery)
            )            
                                               
            candidate_data = []
            for item in queryset:
                row = {
                    'id': item.id,
                    'name': item.name,
                    'mobile':item.mobile,
                    'email': item.email,
                    'post': item.post_name,                    
                    'status': item.status,
                    'percentage': item.percentage,
                    'time_taken': item.time_taken,
                    'status': item.status,
                    'created_at': item.created_at,
                    'Encryp': enc(str(item.id)),                    
                }
                candidate_data.append(row)                     
    except Exception as e:
        print("error-" + e)
        tb = traceback.extract_tb(e.__traceback__)
        fun = tb[0].name
        cursor.callproc("stp_error_log",[fun,str(e),request.user.id])          
    finally:
        cursor.close()
        m.commit()
        m.close()
        Db.closeConnection()
        if request.method == "GET":
            return render(request, "Test/test_index.html",{'data': candidate_data})             