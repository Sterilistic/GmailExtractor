from django.db import models
from django.contrib.auth.models import User
from oauth2client.django_orm import FlowField, CredentialsField
from datetime import date
import datetime
from django.utils import timezone


class FlowModel(models.Model):
	flow = FlowField()


	
class CredentialsModel(models.Model):
	id = models.ForeignKey(User, primary_key=True)
	credential = CredentialsField()

class UserData(models.Model):
	user_id=models.ForeignKey(User)
	label=models.CharField(max_length=500,default='null')
	sender = models.CharField(max_length=500,default="asdf")
	subject = models.CharField(max_length=500,default="asdf")
	body = models.TextField(default="asdf")

class BulkRequestId(models.Model):
	request_id=models.CharField(max_length=500,primary_key=True)	
	label=models.CharField(max_length=500,default="noLabel")
	date = models.DateField( default=timezone.now)

class TaskId(models.Model):
	request_id=models.CharField(max_length=500,primary_key=True)	
	label=models.CharField(max_length=500,default="noLabel")
