import json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login ,logout
from attendance.serializers import *
import Db
from authentication.models import *
from authentication.serializers import * 


def attendance_home(request):
    try:
        user = get_object_or_404(User, id=110000)
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
            status1 = serializer.validated_data['status']
            status_change_time = serializer.validated_data['status_change_time']
            latitude = serializer.validated_data['latitude']
            longitude = serializer.validated_data['longitude']
            param = [employee_id,year,month,day,status1,status_change_time,latitude,longitude]
            cursor.callproc("stp_InsertAttendance",param)
            cursor.close()
            m.commit()
            m.close()
            user = get_object_or_404(User, id=employee_id)
            serializer = UserSerializer(user).data
            user_relation = get_object_or_404(UserRelationMaster, user_id=serializer['id'])
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
                print(str(e))
                return Response( status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)

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




        