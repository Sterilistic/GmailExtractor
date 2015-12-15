import os
import httplib2, base64
from oauth2client.django_orm import Storage
from apiclient.discovery import build
from oauth2client import client
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from .models import UserData
from django.utils.functional import SimpleLazyObject
from django.shortcuts import render, redirect
from .models import CredentialsModel
from .models import BulkRequestId
from .models import TaskId
from django.conf import settings
from django.http import HttpResponse



class ListMails(APIView):
    
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)        
    
    def get(self, request, format=None):
        """
        Handles the  request made by user for bulkdownload and save the request instance in database
        """
        user = request.user
        user_Id = user.username
        label_id = request.GET['label']
        if label_id == "NoLabel":
            message = "Select a folder from the list given in left."
            return HttpResponse(message)
        uid=BulkRequestId.objects.filter(request_id=user_Id, label=label_id)
        if uid:
            message = "Oops! You have already made request for the same folder!"
            return HttpResponse(message)
        else:
            request=BulkRequestId(request_id=user_Id,label=label_id)
            task=TaskId(request_id=user_Id,label=label_id)    # Saving the task id which will run according the scheduler  
            request.save()
            task.save()
            message = "We will send you an Email once the download is ready. You may close this window and continue using our service."
            return HttpResponse(message)
