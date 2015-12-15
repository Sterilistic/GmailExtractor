import httplib2
import base64
from stripogram import html2text
from oauth2client.django_orm import Storage
from apiclient.discovery import build
from oauth2client import client
from django.contrib.auth.models import User
from .models import CredentialsModel
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication
from rest_framework import permissions
from gextracto import models
from gextracto.models import UserData
from gextracto.models import BulkRequestId
from django.template import RequestContext
from rest_framework.response import Response
from django.core import serializers


class ListDownloadRequest(APIView):
    """
    Gets a list of a specified number mail ids for a particular label
    Extracts the email in the form of plain/text
    The API returns all the extracted mails
    """
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        storage = Storage(CredentialsModel, 'id', user, 'credential')
        credentials = storage.get()
        http_auth = credentials.authorize(httplib2.Http())
        service = build('gmail', 'v1', http=http_auth)
        user_Id = user.username
        download_request = BulkRequestId.objects.filter(request_id__startswith = user_Id)
    	request_data = {
    	    "request_detail": download_request
    	}
    	return render(request, 'mydownload.html', request_data, context_instance=RequestContext(request))


class DownloadRequest(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
    	user = request.user
        storage = Storage(CredentialsModel, 'id', user, 'credential')
        credentials = storage.get()
        http_auth = credentials.authorize(httplib2.Http())
        service = build('gmail', 'v1', http=http_auth)
        user_Id = user.username
        label_id = request.GET['label']
        all_mails = UserData.objects.filter(user_id = user, label = label_id).values()
    	return Response(all_mails)


class RemoveData(APIView):
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
    	user = request.user
        storage = Storage(CredentialsModel, 'id', user, 'credential')
        credentials = storage.get()
        http_auth = credentials.authorize(httplib2.Http())
        service = build('gmail', 'v1', http=http_auth)
        user_Id = user.username
        label_id = request.GET['label']
    	BulkRequestId.objects.filter(request_id = user_Id, label = label_id).delete()
    	UserData.objects.filter(user_id=user, label = label_id).delete()
    	return HttpResponse('')
