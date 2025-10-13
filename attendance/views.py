from calendar import monthrange
from datetime import date, datetime
import json
import traceback
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login ,logout
from Account.models import CustomUser, password_storage
from Masters.models import sc_employee_master
from attendance.serializers import *
import Db
from Account.db_utils import callproc
from django.utils.timezone import now
# from authentication.models import *
# from authentication.serializers import * 
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
import io
from .models import EmployeePayroll, Payslip
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse



def attendance_home(request):
    try:
        user = get_object_or_404(CustomUser, id=110000)
        name = user.name  # Assuming your User model has a 'name' field
    except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
    return HttpResponse(f"Attendance Backend {name}")

# Create your views here.
class AttendancePost(APIView):
    def post(self, request):
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        try:
            serializer = AttendanceSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            employee_id = serializer.validated_data['employee_id']
            year = serializer.validated_data['year']
            month = serializer.validated_data['month']
            day = serializer.validated_data['day']
            date_value = date(year, month, day)
            status1 = serializer.validated_data['status']
            status_change_time = serializer.validated_data['status_change_time']
            # time_only = status_change_time.time()
            # formatted_time = time_only.strftime('%H:%M:%S')
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            param = [employee_id,status1,status_change_time,latitude,longitude,date_value]
            cursor.callproc("stp_InsertAttendance",param)
            cursor.close()
            m.commit()
            m.close()
            user = get_object_or_404(CustomUser, username=employee_id)
            serializer = UserSerializer(user).data
            user_relation = get_object_or_404(EmployeeShiftMapping, user_id=serializer['id'])
            shift_instance = get_object_or_404(ShiftMaster, shift_id=user_relation.shift_id)
            in_shift_time = shift_instance.in_shift_time
            out_shift_time = shift_instance.out_shift_time
            api_url = "http://52.172.154.80:8070/AndroidApi/AttedanceMarked"
            payload = {
                "employee_id": str(employee_id),
                "year": str(year),
                "month": str(month),
                "day": str(day),
                "status": str(status1),
                "status_change_time": str(status_change_time),
                "latitude": str(latitude),
                "longitude": str(longitude),
                "in_shift_time": str(in_shift_time),
                "out_shift_time": str(out_shift_time)
            }
            try:
                response = requests.post(api_url, json=payload)
                # Check response status and return appropriate response
                if response.status_code == 200:
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                tb = traceback.extract_tb(e.__traceback__)
                fun = tb[0].name
                callproc("stp_error_log",[fun,str(e),request.user.id])  
                print(f"error: {e}")
        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            callproc("stp_error_log",[fun,str(e),request.user.id])  
            print(f"error: {e}")

class ApplyLeave(APIView):
    def post(self, request):
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        try:
            serializer = LeaveApplySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            employee_id = serializer.validated_data['employee_id']
            from_date = serializer.validated_data['from_date']
            to_date = serializer.validated_data['to_date']
            leave_id = serializer.validated_data['leave_id']
            reason_for_leave = serializer.validated_data['reason_for_leave']
            title = serializer.validated_data['title']
            
            param = [employee_id,from_date,to_date,leave_id,reason_for_leave,title]
            cursor.callproc("stp_InsertLeaveRequest",param)
            inserted_id = ""
            for result in cursor.stored_results():
                data4 = list(result.fetchall()) 
                print(data4)
                for i in data4:
                    inserted_id = i[0]
            cursor.close()
            m.commit()
            m.close()
            api_url = "http://52.172.154.80:8070/AndroidApi/ApplyLeave"
            payload = {
                "employee_id": str(employee_id),
                "from_date": str(from_date),
                "to_date": str(to_date),
                "leave_id": str(leave_id),
                "reason_for_leave": str(reason_for_leave),
                "title": str(title),
                "leave_application_id": str(inserted_id),
            }
            try:
                response = requests.post(api_url, json=payload)
                # Check response status and return appropriate response
                if response.status_code == 200:
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(str(e))
                return Response( status=status.HTTP_400_BAD_REQUEST)
            # Manually check the provided username and password
            # return Response( status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
class ApplyCorrection(APIView):
    def post(self, request):
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        try:
            serializer = ApplyCorrectionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            title = serializer.validated_data['title']
            correction_date = serializer.validated_data['correction_date']
            corrected_time = serializer.validated_data['corrected_time']
            reason_for_correction = serializer.validated_data['reason_for_correction']
            employee_id = serializer.validated_data['employee_id']
            correction_type = serializer.validated_data['type']
            
            param = [title,correction_date,corrected_time,reason_for_correction,employee_id,correction_type]
           
            cursor.callproc("stp_insertTimeCorrection",param)
            inserted_id = ""
            for result in cursor.stored_results():
                data4 = list(result.fetchall()) 
            
                for i in data4:
                    inserted_id = i[0]
            
            cursor.close()
            m.commit()
            m.close()
            
            api_url = "http://52.172.154.80:8070/AndroidApi/AttendanceCorrection"
            payload = {
                "title": str(title),
                "correction_date":str(correction_date) ,
                "corrected_time": str(corrected_time),
                "reason_for_correction": str(reason_for_correction),
                "employee_id": str(employee_id),
                "correction_type": str(correction_type),
                "correction_id":str(inserted_id) ,
           
            }
            try:
                response = requests.post(api_url, json=payload)
                
                # Check response status and return appropriate response
                print(response.status_code)
                if response.status_code == 200:
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(str(e))
                return Response( status=status.HTTP_400_BAD_REQUEST)
            # Manually check the provided username and password
            # return Response( status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
class ApplyEarlyLeave(APIView):
    def post(self, request):
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        try:
            serializer = EarlyLeaveApplySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            employee_id = serializer.validated_data['employee_id']
            leave_date = serializer.validated_data['leave_date']
            leave_time = serializer.validated_data['leave_time']
            reason_for_leave = serializer.validated_data['reason_for_leave']
            title = serializer.validated_data['title']
            
            param = [employee_id,leave_date,leave_time,reason_for_leave,title]
            cursor.callproc("stp_InsertEarlyLeaveRequest",param)
            inserted_id = ""
            for result in cursor.stored_results():
                data4 = list(result.fetchall()) 
                print(data4)
                for i in data4:
                    inserted_id = i[0]
            
            cursor.close()
            m.commit()
            m.close()
            
            api_url = "http://52.172.154.80:8070/AndroidApi/EarlyLeaveRequest"
            try:
                payload = {
                    "employee_id": str(employee_id),
                    "leave_date": str(leave_date),
                    "leave_time": str(leave_time),
                    "reason_for_leave": str(reason_for_leave),
                    "title": str(title),
                    "early_leave_id": str(inserted_id),
            
                }
                response = requests.post(api_url, json=payload)
                
                # Check response status and return appropriate response
                if response.status_code == 200:
                    return Response("ghdfjhj")
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print(str(e))
                return Response( status=status.HTTP_400_BAD_REQUEST)
            # Manually check the provided username and password
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
def FetchRecentAttendance(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    data5 = []
    user_id = request.GET.get('user_id', '')
    params = [user_id]
    cursor.callproc("stp_fetchRecentAttendance",params)
    for result in cursor.stored_results():
        data4 = list(result.fetchall()) 
        print(data4)
        for i in data4:
            recent_attendance_dict = {
                'shiftType': i[3],
                'shiftDate': i[0],
                'shiftStartTime': i[1],
                'shiftEndTime': i[2],
            }
            data5.append(recent_attendance_dict)
                                        


    # Return the result as JSON

    return JsonResponse(data5,safe=False)
def FetchRecentLeaves(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    data5 = []
    user_id = request.GET.get('user_id', '')
    params = [user_id]
    cursor.callproc("stp_FetchRecentLeaves",params)
    for result in cursor.stored_results():
        data4 = list(result.fetchall()) 
        for i in data4:
            recent_leave_dict = {
                'title': i[0],
                'leave_id': i[1],
                'from_date': i[2],
                'to_date': i[3],
                'reason_for_leave': i[4],
                'leave_status': i[5],
            }
            data5.append(recent_leave_dict)
                                        


    # Return the result as JSON

    return JsonResponse(data5,safe=False)
def FetchCurrentAttendance(request):
    Db.closeConnection()
    m = Db.get_connection()
    cursor=m.cursor()
    data5 = []
    user_id = request.GET.get('user_id', '')
    params = [user_id]
    cursor.callproc("stp_getCurentAttendance",params)
    for result in cursor.stored_results():
        data4 = list(result.fetchall()) 
        for i in data4:
            a = str(i[0])+"&&"+str(i[1])+"&&"+str(i[2])+"&&"+str(i[3])
            data5.append(a)
        
                                        


    # Return the result as JSON
    return JsonResponse(data5,safe=False)

def GetLeaveTypeList(request):
    api_url = "http://52.172.154.80:8070/AndroidApi/LeaveTypeList"
    try:
        response = requests.get(api_url)
        # Check response status and return appropriate response
        if response.status_code == 200:
            data = response.json()
            # Decode the JSON string and convert it into the desired format
            leave_type = [{'leavetype': item['leavetype'], 'leavedescription': item['leavedescription']} for item in json.loads(data['List1'])]
            return JsonResponse(leave_type,safe=False)
            # return Response(response.body, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
            print(str(e))
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            callproc("stp_error_log",[fun,str(e),request.user.id])  
            print(f"error: {e}")
            return Response( status=status.HTTP_400_BAD_REQUEST)
    
def getAlertList(request):
    try:
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        data5 = []
        user_id = request.GET.get('user_id', '')
        params = [user_id]
        cursor.callproc("stp_fetchUserAlerts",params)
        for result in cursor.stored_results():
            data4 = list(result.fetchall()) 
            print(data4)
            for i in data4:
                alerts = {
                    'id': i[0],
                    'alert_text': i[1],
                }
                data5.append(alerts)
    # Return the result as JSON
        return JsonResponse(data5,safe=False) 
    except Exception as e:
        print(str(e))
        return Response( status=status.HTTP_400_BAD_REQUEST)
    
class GetAlertList(APIView):
    def get(self,request, employee_id):
        try:
            if not employee_id:
                return Response(
                    {"message": "employee_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Fetch alerts for the employee
            alerts = Alerts.objects.filter(employee_id=employee_id).order_by("-created_at")

            if not alerts.exists():
                return Response(
                    {"message": "No alerts found for this employee"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = AlertSerializer(alerts, many=True)
            return Response(
                {"alerts": serializer.data, "count": alerts.count()},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    
class LeaveStatusUpdate(APIView):
    def post(self, request):
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        try:
            serializer = LeaveStatusUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            leave_master_id = serializer.validated_data['id']
            status_value = serializer.validated_data['status']
            param = [leave_master_id,status_value]
            cursor.callproc("stp_updateLeaveStatus",param)
            cursor.close()
            m.commit()
            m.close()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)

class AttendanceCorrectionUpdate(APIView):
    def post(self, request):
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        try:
            serializer = LeaveStatusUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            leave_master_id = serializer.validated_data['id']
            status_value = serializer.validated_data['status']
            param = [leave_master_id,status_value]
            cursor.callproc("stp_updateAttendanceCorrectionStatus",param)
            cursor.close()
            m.commit()
            m.close()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
class AlertsPost(APIView):
    def post(self, request):
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        try:
            serializer = AlertSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            employee_id = serializer.validated_data['employee_id']
            text = serializer.validated_data['text']
            param = [employee_id,text]
            cursor.callproc("stp_createAlert",param)
            cursor.close()
            m.commit()
            m.close()
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)        
        
class ApplyLeaveESS(APIView):
    def post(self, request):
        Db.closeConnection()
        m = Db.get_connection()
        cursor=m.cursor()
        try:
            serializer = LeaveApplySerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            employee_id = serializer.validated_data['employee_id']
            from_date = serializer.validated_data['from_date']
            to_date = serializer.validated_data['to_date']
            leave_id = serializer.validated_data['leave_id']
            reason_for_leave = serializer.validated_data['reason_for_leave']
            title = serializer.validated_data['title']
            
            param = [employee_id,from_date,to_date,leave_id,reason_for_leave,title]
            cursor.callproc("stp_InsertLeaveRequest",param)
            inserted_id = ""
            for result in cursor.stored_results():
                data4 = list(result.fetchall()) 
                print(data4)
                for i in data4:
                    inserted_id = i[0]
            cursor.close()
            m.commit()
            m.close()
            response_data = {'id': inserted_id}
            return JsonResponse(data=response_data, status=status.HTTP_200_OK)
             
            # Manually check the provided username and password
            # return Response( status=status.HTTP_200_OK)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
        

class LoginView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Manually check the provided username and password
            user = get_object_or_404(CustomUser, username=username)

            if user.check_password(password):
                # login(request, user)
                serializer = UserSerializer(user).data
                user_details = get_object_or_404(sc_employee_master, employee_id=serializer['username'])
                user_relation = get_object_or_404(EmployeeShiftMapping, employee_id=serializer['username'])
        
                # Accessing the related LocationMaster instance using the ForeignKey
                location_instance = get_object_or_404(site_master, site_id=user_details.site_id.site_id)
                shift_instance = get_object_or_404(ShiftMaster, shift_id=user_relation.shift_id)
                # Extracting latitude and longitude from the related LocationMaster instance
                latitude = location_instance.latitude
                longitude = location_instance.longitude
                in_shift_time = shift_instance.in_shift_time
                out_shift_time = shift_instance.out_shift_time
                company_id = user_details.company_id.company_id
                company_name = user_details.company_id.company_name
                site_name = user_details.site_id.site_name
                site_id = user_details.site_id.site_id
                serializer["company_id"] = company_id
                serializer["site_id"] = site_id
                serializer["latitude"] = latitude
                serializer["longitude"] = longitude
                serializer["company_name"] = company_name
                serializer["site_name"] = site_name
                serializer["in_shift_time"] = in_shift_time
                serializer["out_shift_time"] = out_shift_time
                
                return JsonResponse(serializer, status=status.HTTP_200_OK,safe=False)
            else:
                return JsonResponse({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED,safe=False)
            
        except Exception as e:
            print(str(e))
            tb = traceback.extract_tb(e.__traceback__)
            fun = tb[0].name
            callproc("stp_error_log",[fun,str(e),request.user.id])  
            print(f"error: {e}")
            return Response( status=status.HTTP_400_BAD_REQUEST)
        
class RegistrationView(APIView):
    def post(self, request):
        try:
            serializer = RegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            raw_password = serializer.validated_data.get('password')
            user = CustomUser.objects.create(**serializer.validated_data)
            user.set_password(raw_password)
            user.save()
            password_storage.objects.create(user=user, passwordText=raw_password)
            
            serializer = UserSerializer(user).data
            serializer["latitude"] = ""
            serializer["longitude"] =  ""
            serializer["in_shift_time"] = ""
            serializer["out_shift_time"] =  ""
            return JsonResponse(serializer, status=status.HTTP_200_OK,safe=False)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
        
class getUserDetails(APIView):
    def post(self, request):
        try:
            # print(request.data)
            user = get_object_or_404(CustomUser, username=request.data["user_id"])

            serializer = UserSerializer(user).data
            user_details = get_object_or_404(sc_employee_master, employee_id=serializer['username'])
            user_relation = get_object_or_404(EmployeeShiftMapping, employee_id=serializer['username'])
    
            # Accessing the related LocationMaster instance using the ForeignKey
            location_instance = get_object_or_404(site_master, site_id=user_details.site_id.site_id)
            shift_instance = get_object_or_404(ShiftMaster, shift_id=user_relation.shift_id)
            # Extracting latitude and longitude from the related LocationMaster instance
            latitude = location_instance.latitude
            longitude = location_instance.longitude
            in_shift_time = shift_instance.in_shift_time
            out_shift_time = shift_instance.out_shift_time
            company_id = shift_instance.company_id.company_id
            site_id = location_instance.site_id
            serializer["company_id"] = company_id
            serializer["site_id"] = site_id
            serializer["latitude"] = latitude
            serializer["longitude"] = longitude
            serializer["in_shift_time"] = in_shift_time
            serializer["out_shift_time"] = out_shift_time
            
            return JsonResponse(serializer, status=status.HTTP_200_OK,safe=False)
            # return JsonResponse([], status=status.HTTP_200_OK,safe=False)
            
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
        
class AttendanceLogInsert(APIView):
    def post(self, request):
        try:
            serializer = AttendanceLogSerializer(data=request.data)
            
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Attendance log created successfully','data': serializer.data}, status=status.HTTP_201_CREATED)
            
            else:
                print("Validation Errors:", serializer.errors)
                return Response({ 'message': 'Validation Failed','errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Unexpected Error:", str(e))
            return Response({'message': 'Internal Server Error','error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class getLocationDropdown(APIView):
    def post(self, request):
        try:
            # Fetch active sites
            emp_id = request.data["employee_id"] 
            company_id = get_object_or_404(sc_employee_master , employee_id= emp_id).company_id      
            # sites = site_master.objects.filter(is_active=True, company_id=company_id ).values('site_id', 'site_name')
            sites = site_master.objects.filter(
                is_active=True, company_id=company_id
            ).values('site_id', 'site_name', 'latitude', 'longitude')
            

            # Convert QuerySet to list
            site_list = list(sites)

            return JsonResponse(site_list, status=status.HTTP_200_OK, safe=False)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)    
        

from datetime import date
from calendar import monthrange
class GetCalendarData(APIView):
    def post(self, request):
        employee_id = request.data.get("employee_id")
        year = request.data.get("year")

        if not (employee_id and year):
            return JsonResponse({"error": "Missing parameters"}, status=400)

        try:
            year = int(year)
        except ValueError:
            return JsonResponse({"error": "Year should be an integer"}, status=400)

        # Helper: get all dates for given month
        def get_all_dates(year, month):
            num_days = monthrange(year, month)[1]
            return [date(year, month, day) for day in range(1, num_days + 1)]

        # Collect all dates for the full year
        all_dates = []
        for m in range(1, 13):
            all_dates.extend(get_all_dates(year, m))

        # Fetch attendance records for the full year
        attendance_records = DailyAttendance.objects.filter(
            employee_id=employee_id,
            atten_date__year=year
        )

        # Dict for quick lookup
        attendance_dict = {
            record.atten_date: {
                "is_present": record.is_present,
                "in_time": record.in_time.strftime("%H:%M:%S") if record.in_time else None,
                "out_time": record.out_time.strftime("%H:%M:%S") if record.out_time else None,
            }
            for record in attendance_records
        }

        today = date.today()
        attendance_list = []

        for day in all_dates:
            if day > today:  # Future
                status = "future"
                in_time = None
                out_time = None
            elif day == today:  # Today
                if day in attendance_dict:
                    status = "present" if attendance_dict[day]["is_present"] else "absent"
                    in_time = attendance_dict[day]["in_time"] if status == "present" else None
                    out_time = attendance_dict[day]["out_time"] if status == "present" else None
                else:
                    status = "today"
                    in_time = None
                    out_time = None
            elif day.weekday() == 6:  # Sunday
                status = "sunday"
                in_time = None
                out_time = None
            elif day in attendance_dict:  # Attendance available
                status = "present" if attendance_dict[day]["is_present"] else "absent"
                in_time = attendance_dict[day]["in_time"] if status == "present" else None
                out_time = attendance_dict[day]["out_time"] if status == "present" else None
            else:  # No record
                status = "absent"
                in_time = None
                out_time = None

            attendance_list.append({
                "date": day.strftime("%Y-%m-%d"),
                "status": status,
                "in_time": in_time,
                "out_time": out_time,
            })

        return JsonResponse({"attendance": attendance_list})

    
class LeaveList(APIView):

    def post(self, request):
        try:
            employee_id = request.data["employee_id"]
            filter_type = request.data["type"] # "month" or "year"
            today = now()

            if not employee_id or not filter_type:
                return Response({"error": "employee_id and type are required"}, status=400)

            # Convert employee_id to int
            employee_id = int(employee_id)

            if filter_type == "month":
                leaves = LeaveApply.objects.filter(
                    employee_id=employee_id,
                    from_date__year=today.year,
                    from_date__month=today.month
                )
            elif filter_type == "year":
                leaves = LeaveApply.objects.filter(
                    employee_id=employee_id,
                    from_date__year=today.year
                )
            else:
                return Response({"error": "Invalid type"}, status=400)

            serializer = LeaveApplySerializer(leaves, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class LeaveDashboardView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            employee_id = request.data.get("employee_id")

            if not employee_id:
                return JsonResponse({"error": "employee_id is required"}, status=400)

            # Step 1: Get leave types from external API
            try:
                response = requests.get("http://52.172.154.80:8070/AndroidApi/LeaveTypeList")
                leave_types = response.json()

                # Case 1: If API returned dict with key "List1" that contains JSON string
                if isinstance(leave_types, dict):
                    for val in leave_types.values():
                        if isinstance(val, str):
                            leave_types = json.loads(val)   # convert string to list of dicts
                            break

                # Case 2: If API returned string directly
                elif isinstance(leave_types, str):
                    leave_types = json.loads(leave_types)

                # Now it's guaranteed to be a list of dicts
                leave_dashboard = {lt["leavedescription"]: 0 for lt in leave_types}   # this is a list of dicts
            except Exception as e:
                return JsonResponse({"error": f"Failed to fetch leave types: {str(e)}"}, status=500)

            leaves = LeaveApply.objects.filter(employee_id=employee_id)

            # Step 4: Count leaves by type
            for leave in leaves:
                if leave.leave_id in leave_dashboard:
                    leave_dashboard[leave.leave_id] += 1
                else:
                    # Handle unexpected leave names
                    leave_dashboard[leave.leave_id] = leave_dashboard.get(leave.leave_id, 0) + 1

            # Step 5: Return only counts
            return Response({
                "employee_id": employee_id,
                "leave_summary": leave_dashboard
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PaySlipList(APIView):
    def get(self, request, *args, **kwargs):
        try:
            employee_id = kwargs.get("employee_id")
            payslips = Payslip.objects.filter(employee_id=employee_id).values(
                "id", "name", "year", "month"
            )
            return Response({"payslips": list(payslips)}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


from reportlab.platypus import Image

try:
    pdfmetrics.registerFont(TTFont("Poppins", "static/fonts/Poppins-Regular.ttf"))
    pdfmetrics.registerFont(TTFont("Poppins-Bold", "static/fonts/Poppins-Bold.ttf"))
    pdfmetrics.registerFont(TTFont("Poppins-SemiBold", "static/fonts/Poppins-SemiBold.ttf"))
    pdfmetrics.registerFont(TTFont("Poppins-Italic", "static/fonts/Poppins-Italic.ttf"))
    base_font = "Poppins"
    bold_font = "Poppins-Bold"
    semi_font = "Poppins-SemiBold"
    italic_font = "Poppins-Italic"
except:
    # Fallback to Helvetica if custom fonts missing
    base_font = "Helvetica"
    bold_font = "Helvetica-Bold"
    semi_font = "Helvetica-Bold"
    italic_font = "Helvetica-Oblique"


class GeneratePayslipPDF(APIView):
    def post(self, request, *args, **kwargs):
        try:
            payslip_id = request.data.get("id")
            employee_id = request.data.get("employee_id")
            year = request.data.get("year")
            month = request.data.get("month")

            # Get employee
            employee = sc_employee_master.objects.get(employee_id=employee_id)

            # Payroll details
            payrolls = EmployeePayroll.objects.filter(
                employee_id=employee_id, year=year, month=month
            ).values("parameter_name", "parameter_value", "type_of_pay_element", "recovery_amount")

            # Get earnings, deductions
            earnings = [(p["parameter_name"], p["parameter_value"]) for p in payrolls if p["type_of_pay_element"] == "Earning" and p["parameter_value"] > 0]
            deductions = [(p["parameter_name"], p["parameter_value"]) for p in payrolls if p["type_of_pay_element"] == "Deduction" and p["parameter_value"] > 0]

            # Totals
            total_earning = next((p for p in payrolls if p["type_of_pay_element"] == "Total Earning"), None)
            total_deduction = next((p for p in payrolls if p["type_of_pay_element"] == "Total Deduction"), None)
            net_salary = next((p for p in payrolls if p["type_of_pay_element"] == "Net Salary"), None)

            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=30, bottomMargin=30, leftMargin=25, rightMargin=25)
            styles = getSampleStyleSheet()

            # Custom styles
            styles.add(ParagraphStyle(name="Header", alignment=1, fontSize=18, leading=22, fontName=bold_font, spaceAfter=10))
            styles.add(ParagraphStyle(name="SubHeader", alignment=1, fontSize=13, leading=16, fontName=semi_font, spaceAfter=8))
            styles.add(ParagraphStyle(name="Center", alignment=1, fontSize=11, fontName=base_font))
            styles.add(ParagraphStyle(name="Right", alignment=2, fontSize=11, fontName=base_font))
            styles.add(ParagraphStyle(name="Footer", alignment=1, fontSize=9, fontName=italic_font, textColor=colors.HexColor("#7f8c8d")))

            elements = []

            # ==== Date on right side ====
            month_names = {
                "1": "JAN", "2": "FEB", "3": "MAR", "4": "APR", "5": "MAY", "6": "JUN",
                "7": "JUL", "8": "AUG", "9": "SEP", "10": "OCT", "11": "NOV", "12": "DEC"
            }
            display_month = month_names.get(str(month), str(month))
            
            date_table = Table([[f"{display_month} {year}"]], colWidths=[500])
            date_table.setStyle(TableStyle([
                ("ALIGN", (0,0), (0,0), "RIGHT"),
                ("FONTNAME", (0,0), (0,0), bold_font),
                ("FONTSIZE", (0,0), (0,0), 12),
                ("BOTTOMPADDING", (0,0), (0,0), 10),
            ]))
            elements.append(date_table)

            # ==== Company Header ====
            logo_path = "static/images/pmc.png"   
            try:
                img = Image(logo_path, width=80, height=70)
                img.hAlign = "CENTER"
                elements.append(img)
            except:
                pass

            elements.append(Paragraph("<b>HRMS Panvel.</b>", styles["Header"]))
            elements.append(Paragraph("PAY SLIP", styles["SubHeader"]))
            elements.append(Spacer(1, 15))

            # ==== Employee Info Table ====
            emp_data = [
                ["Employee:", employee.employee_name, "Employee ID:", str(employee_id)],
                ["Department:", getattr(employee, "department", "N/A"), "Designation:", getattr(employee, "designation", "N/A")],
                ["Bank:", getattr(employee, "bank_name", "N/A"), "Account No:", getattr(employee, "account_no", "N/A")],
                ["ESIC No:", getattr(employee, "esic", "N/A"), "PF No:", getattr(employee, "pf_no", "N/A")]
            ]

            emp_table = Table(emp_data, colWidths=[90, 150, 90, 150])
            emp_table.setStyle(TableStyle([
                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("FONTNAME", (0,0), (-1,-1), base_font),
                ("FONTSIZE", (0,0), (-1,-1), 10),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
                ("BACKGROUND", (0,0), (-1,0), colors.whitesmoke),

                # Add spacing inside each cell
                ("LEFTPADDING", (0,0), (-1,-1), 6),
                ("RIGHTPADDING", (0,0), (-1,-1), 6),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ]))
            elements.append(emp_table)
            elements.append(Spacer(1, 15))

            # ==== Earnings & Deductions ====
            max_rows = max(len(earnings), len(deductions))
            earnings_filled = earnings + [("", 0)] * (max_rows - len(earnings))
            deductions_filled = deductions + [("", 0)] * (max_rows - len(deductions))

            data = [["Allowances", "Amount", "Deductions", "Amount"]]
            for i in range(max_rows):
                data.append([
                    earnings_filled[i][0], 
                    f"{earnings_filled[i][1]:.2f}" if earnings_filled[i][1] else "",
                    deductions_filled[i][0], 
                    f"{deductions_filled[i][1]:.2f}" if deductions_filled[i][1] else ""
                ])

            total_earning_value = total_earning["parameter_value"] if total_earning else sum([t[1] for t in earnings])
            total_deduction_value = total_deduction["parameter_value"] if total_deduction else sum([t[1] for t in deductions])
            net_salary_value = net_salary["parameter_value"] if net_salary else (total_earning_value - total_deduction_value)

            data.append(["Total Earning", f"{total_earning_value:.2f}", "Total Deduction", f"{total_deduction_value:.2f}"])
            data.append(["Net Salary", f"{net_salary_value:.2f}", "", ""])

            table = Table(data, colWidths=[180, 80, 180, 80])
            table.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (1,0), colors.HexColor("#2c3e50")),
                ("BACKGROUND", (2,0), (3,0), colors.HexColor("#2c3e50")),
                ("TEXTCOLOR", (0,0), (-1,0), colors.white),
                ("FONTNAME", (0,0), (-1,0), bold_font),
                ("FONTSIZE", (0,0), (-1,0), 11),

                ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
                ("FONTNAME", (0,1), (-1,-3), base_font),
                ("FONTSIZE", (0,1), (-1,-3), 10),
                ("ALIGN", (1,1), (1,-1), "RIGHT"),
                ("ALIGN", (3,1), (3,-1), "RIGHT"),

                # Add padding inside table cells
                ("LEFTPADDING", (0,0), (-1,-1), 6),
                ("RIGHTPADDING", (0,0), (-1,-1), 6),
                ("TOPPADDING", (0,0), (-1,-1), 4),
                ("BOTTOMPADDING", (0,0), (-1,-1), 4),

                ("BACKGROUND", (0,-2), (1,-2), colors.HexColor("#ecf0f1")),
                ("BACKGROUND", (2,-2), (3,-2), colors.HexColor("#ecf0f1")),
                ("FONTNAME", (0,-2), (-1,-2), semi_font),
                ("FONTSIZE", (0,-2), (-1,-2), 11),

                ("BACKGROUND", (0,-1), (-1,-1), colors.HexColor("#27ae60")),
                ("TEXTCOLOR", (0,-1), (-1,-1), colors.white),
                ("FONTNAME", (0,-1), (-1,-1), bold_font),
                ("FONTSIZE", (0,-1), (-1,-1), 13),
                ("ALIGN", (1,-1), (1,-1), "RIGHT"),
                ("ALIGN", (0,-1), (0,-1), "LEFT"),
            ]))

            elements.append(table)
            elements.append(Spacer(1, 20))

            # Footer
            elements.append(Paragraph("This is a computer generated payslip and does not require signature.", styles["Footer"]))

            doc.build(elements)
            buffer.seek(0)
            response = HttpResponse(buffer, content_type="application/pdf")
            response["Content-Disposition"] = f'attachment; filename=\"payslip_{employee_id}_{month}_{year}.pdf\"'
            return response

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)