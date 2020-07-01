from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from accounts.models import User
from django.shortcuts import get_object_or_404
from accounts.api.serializers import (
    RegistrationSerializer,OTPSerializer,LoginSerializer
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from accounts.authy_api import send_verfication_code,verify_sent_code
from rest_framework.authtoken.models import Token
import json





class register(CreateAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            fullname = serializer.validated_data['full_name']
            phonenumber = serializer.validated_data['phone_number']
            countrycode = serializer.validated_data['country_code']
            otp = serializer.validated_data['otp']
            already = User.objects.filter(phone_number=phonenumber)
            if already:
                dict = { 'status':'user already exists'}
                return Response(dict)
            user = { 'phone_number': phonenumber, 'country_code': countrycode, 'full_name': fullname}
            response = verify_sent_code(otp, user)
            data = json.loads(response.text)
            if data['success'] == True:

                account=serializer.save()
                token = Token.objects.get(user=account).key
                group = Group.objects.get(name='customer')
                account.groups.add(group)
                dict ={ 'user': user, 'status': 'registered','token':token,'success':'True'}
                return Response(dict)
            else:
                dict ={ 'user': user, 'status': 'unregistered','success':'False' }
                return Response(dict)


class otp(CreateAPIView):
    serializer_class = OTPSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            phonenumber = serializer.validated_data['phone_number']
            countrycode = serializer.validated_data['country_code']
            user = { 'phone_number': phonenumber, 'country_code': countrycode }
            response = send_verfication_code(user)
            data = json.loads(response.text)

            if data['success'] == False:
                dict = {'status': 'OTP not send! Try Again', 'success': 'False'}
                return Response(dict)
            else:
                dict = { 'status': 'OTP Sent successfully', 'phone_number': phonenumber, 'success': 'True'}
                return Response(dict)
        else:
            data = serializer.errors
            return Response(data)


class otp_with_param(CreateAPIView):
    serializer_class = OTPSerializer
    def get(self, request, format=None):
            phone_number = request.query_params['phone_number']
            country_code = request.query_params['country_code']
            user = { 'phone_number': phonenumber, 'country_code': countrycode }
            response = send_verfication_code(user)
            data = json.loads(response.text)

            if data['success'] == False:
                dict = {'status': 'OTP not send! Try Again', 'success': 'False'}
                return Response(dict)
            else:
                dict = { 'status': 'OTP Sent successfully', 'phone_number': phonenumber, 'success': 'True'}
                return Response(dict)
         



class login(CreateAPIView):
    serializer_class = LoginSerializer

    def post(self,request,format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            phonenumber = serializer.validated_data['phone_number']
            countrycode = serializer.validated_data['country_code']
            user = { 'phone_number': phonenumber, 'country_code': countrycode }
            try:
                userob=User.objects.filter(phone_number=phonenumber)[0]
                token, _ = Token.objects.get_or_create(user=userob)
            except:
                return Response({'status':'User does not exist','success':'False'})
            otp = serializer.validated_data['otp']
            response = verify_sent_code(otp, user)
            data = json.loads(response.text)
            if data['success'] == True:
                return Response({'user':user,'token': token.key,'status':'Token Generated','success':'True'})
            else:
                return Response({'status':'OTP entered is not valid','success':'False'})
