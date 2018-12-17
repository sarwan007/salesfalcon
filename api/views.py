from django.shortcuts import render
from .models import (
    UserProfile,
    Customer,
    DeliveredMessage,
    MeetingNote,
    MeetingReminder
)
from .serializers import (
    UserSerializer,
    UserProfileSerializer,
    UserDetailsSerializer,
    PotentialCustomerSerializer,
    CustomerSerializer,
    PutDeliveredMessageSerializer,
    FetchDeliveredMessageSerializer,
    SaveMeetingNotesSerializer,
    FetchMeetingNotesSerializer,
    ReminderNotesSerializer,
    FetchMeetingReminderSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from rest_framework.parsers import FileUploadParser
from django.core.mail import send_mass_mail, send_mail, BadHeaderError
import random


class UserRegistration(APIView):
    """
    List the details of user
    """
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        user = request.data
        user['username'] = 'sf' + str(random.randint(1, 100)) + '_' + \
                           user['first_name'] + '_' + user['last_name']

        if User.objects.filter(email=user['email']).exists():
            return Response({"message": "user already exists"})

        user_serializer = UserSerializer(data=user)

        if user_serializer.is_valid():
            user_instance = user_serializer.save()
            login(request, user_instance)
            token = Token.objects.create(user=user_instance)
            return Response({
                "Message": "User registered successfully",
                "user": user_serializer.data,
                "token": token.key
            })
        return Response(user_serializer.errors)


class UserDetails(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        user_details_serializer = UserProfileSerializer(data=request.data)
        if user_details_serializer.is_valid():
            user_details_serializer.save(owner=request.user)
            return Response(user_details_serializer.data)
        return Response(user_details_serializer.errors)

    def put(self, request, format=None):
        user_profile = UserProfile.objects.get(owner=request.user)
        user_details_serializer = UserProfileSerializer(user_profile, data=request.data)
        if user_details_serializer.is_valid():
            user_details_serializer.save()
            return Response({"message": "Updated Successfully",
                             "user": user_details_serializer.data})
        return Response(user_details_serializer.errors)

    def get(self, request, format=None):
        user = UserProfile.objects.get(owner=request.user)
        serializer = UserDetailsSerializer(user)
        return Response(serializer.data)


class Login(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        email = request.data['email']
        username = User.objects.get(email=email).username
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"message": "Success",
                             "token": token.key})
        else:
            return Response({"message": "register please"})


class Logout(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        Token.objects.get(user=request.user).delete()
        logout(request)
        return Response({"message": "Successfully logout"})


class FileUpload(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        # TODO : Send to s3 bucket
        return Response(status=204)


class CustomerDetails(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        potential_customer_serializer = PotentialCustomerSerializer(data=request.data, many=True)
        if potential_customer_serializer.is_valid():
            potential_customer_serializer.save(owner=request.user)
            return Response(potential_customer_serializer.data)
        else:
            return Response(potential_customer_serializer.errors)

    def get(self, request, format=None):
        customers = Customer.objects.filter(owner=request.user)
        customer_details_serializer = CustomerSerializer(customers, many=True)
        return Response(customer_details_serializer.data)


class SendEmail(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        sender = request.user.email
        message_type = request.data.get('message_type', '')
        message = request.data.get('message', '')
        receiver = request.data.get('receiver', '')
        subject = request.data.get('subject', '')
        if message_type == 'BULK' and subject and message and receiver:
            bulk_message = (subject, message, sender, receiver)
            try:
                send_mass_mail((bulk_message,))
            except BadHeaderError:
                return Response({"error": "Invalid Headers"})
        else:
            try:
                send_mail(subject, message, sender, receiver)
            except BadHeaderError:
                return Response({"error": "Invalid Headers"})

        message_serializer = PutDeliveredMessageSerializer(data=request.data)

        if message_serializer.is_valid():
            message_serializer.save(owner=request.user)
            return Response({"message": "success"})
        return Response({"message": "error", "error": message_serializer.errors})

    def get(self, request, format=None):
        messages = DeliveredMessage.objects.filter(owner=request.user)
        message_serializer = FetchDeliveredMessageSerializer(messages, many=True)
        return Response(message_serializer.data)


class MeetingNotesView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, format=None):
        potential_customer = Customer.objects.get(phone_no=request.data['customer']['phone_no'],
                                                  email=request.data['customer']['email'])
        request.data.pop('customer')
        serializer = SaveMeetingNotesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=potential_customer)
            return Response(serializer.data)
        return Response(serializer.errors)

    def put(self, request, format=None):
        note = MeetingNote.objects.get(pk=request.query_params['id'])
        serializer = SaveMeetingNotesSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Notes updated successfully",
                             "notes": serializer.data})
        return Response(serializer.errors)

    def delete(self, request, format=None):
        MeetingNote.objects.get(pk=request.query_params['id']).delete()
        return Response({"message": "delete successfully"})

    def get(self, request, format=None):
        potential_customer = Customer.objects.get(phone_no=request.query_params['phone_no'])
        notes = MeetingNote.objects.get(customer=potential_customer)
        return Response(FetchMeetingNotesSerializer(notes).data)


class SetReminderView(APIView):

    def post(self, request, format=None):
        customer = Customer.objects.get(pk=request.data['customer_id'])
        note = MeetingNote.objects.filter(customer=customer, flag=request.data['flag'])
        request.data.pop('customer_id')
        request.data.pop('flag')
        serializer = ReminderNotesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, note=note)
            return Response(serializer.data)
        return Response(serializer.errors)

    def put(self, request, format=None):
        reminder = MeetingReminder.objects.get(pk=request.query_params['id'])
        serializer = ReminderNotesSerializer(reminder, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

    def get(self, request, format=None):
        reminders = MeetingReminder.objects.get(user=request.user)
        return Response(FetchMeetingReminderSerializer(reminders, many=True).data)
