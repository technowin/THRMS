from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate, login ,logout
from attendance.models import *

import mobile_authen
from .models import PasswordStorage, User
from .serializers import UserSerializer, LoginSerializer, RegistrationSerializer

class LoginView(APIView):
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            # Manually check the provided username and password
            user = get_object_or_404(User, username=username)

            if user.check_password(password):
                login(request, user)
                serializer = UserSerializer(user).data
                user_relation = get_object_or_404(UserRelationMaster, user_id=serializer['id'])
        
                # Accessing the related LocationMaster instance using the ForeignKey
                location_instance = get_object_or_404(LocationMaster, location_id=user_relation.location_id)
                shift_instance = get_object_or_404(ShiftMaster, shift_id=user_relation.shift_id)
                # Extracting latitude and longitude from the related LocationMaster instance
                latitude = location_instance.latitude
                longitude = location_instance.longitude
                in_shift_time = shift_instance.in_shift_time
                out_shift_time = shift_instance.out_shift_time
                serializer["latitude"] = latitude
                serializer["longitude"] = longitude
                serializer["in_shift_time"] = in_shift_time
                serializer["out_shift_time"] = out_shift_time
                
                return JsonResponse(serializer, status=status.HTTP_200_OK,safe=False)
            else:
                return JsonResponse({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED,safe=False)
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
class RegistrationView(APIView):
    def post(self, request):
        try:
            serializer = RegistrationSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            raw_password = serializer.validated_data.get('password')
            user = User.objects.create(**serializer.validated_data)
            user.set_password(raw_password)
            user.save()
            PasswordStorage.objects.create(user=user, raw_password=raw_password)
            
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
            user = get_object_or_404(User, id=request.data["user_id"])

            serializer = UserSerializer(user).data
            user_relation = get_object_or_404(UserRelationMaster, user_id=serializer['id'])
    
            # Accessing the related LocationMaster instance using the ForeignKey
            location_instance = get_object_or_404(LocationMaster, location_id=user_relation.location_id)
            shift_instance = get_object_or_404(ShiftMaster, shift_id=user_relation.shift_id)
            # Extracting latitude and longitude from the related LocationMaster instance
            latitude = location_instance.latitude
            longitude = location_instance.longitude
            in_shift_time = shift_instance.in_shift_time
            out_shift_time = shift_instance.out_shift_time
            serializer["latitude"] = latitude
            serializer["longitude"] = longitude
            serializer["in_shift_time"] = in_shift_time
            serializer["out_shift_time"] = out_shift_time
            
            return JsonResponse(serializer, status=status.HTTP_200_OK,safe=False)
            # return JsonResponse([], status=status.HTTP_200_OK,safe=False)
            
        except Exception as e:
            print(str(e))
            return Response( status=status.HTTP_400_BAD_REQUEST)
    