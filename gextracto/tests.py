from django.test import TestCase, RequestFactory, Client
from django.contrib.auth.models import User
from .api import *
from .views import *
from django.db import models
from oauth2client.django_orm import FlowField, CredentialsField

from rest_framework.test import APIClient

#from extractor.models import CredentialsModel, FlowModel
from .testing_resources.noconflict import classmaker
import ast
import json
from django.conf import settings
from django.utils.importlib import import_module





def step2_exchange(self,*args, **kwargs):
	
	return 3


tem_for_get=FlowModel.objects.get


def get(*args, **kwargs):
	instance=tem_for_get(*args, **kwargs)
	instance.flow.step2_exchange=step2_exchange
	return instance
FlowModel.objects.get=get

class CheckAuth(TestCase):
	def setUp(self):
		self.factory = RequestFactory()
		self.c = Client()
		self.c.session['temp'] = 'asdfas'
		self.user = User.objects.create_user(username='test_user1@gmail.com', password='test_user1_password')
		
		
	def test_correct_credentials(self):
		"""
		user authentication with correct credentials
		"""
		
		response = self.c.post('/login/', {'email': 'test_user1@gmail.com', 'password': 'test_user1_password'})
		self.assertRedirects(response, 'http://testserver/email-extractor/')
		
		
	def test_wrong_password(self):
		"""
		User authentication with wrong password
		"""
		
		response = self.c.post('/login/', {'email': 'test_user1@gmail.com', 'password': 'test_user1_wrong_password'})
		self.assertTemplateUsed(response, 'homepage.html')
		self.assertContains(response, 'Invalid username or password')
		




		
class MailsExtraction(TestCase):
	def setUp(self):
		self.api_client = APIClient()
		self.api_client.login(username = 'test_user1@gmail.com', password = 'test_user1_password')
		self.list_mails = ListMails()
		
		self.message_types = ('multipart_alternative', 'multipart_mixed', 'text_html')
		#self.message_types = ('multipart_alternative', 'multipart_related', 'multipart_mixed', 'text_html')
		

	def message_body(self, message, message_type):
		"""
		extracting the body given the entire message dictionary
		"""
		
		body = self.list_mails.get_message_body(message)
		with open('extractor/testing_resources/body/'+ message_type + '.json', 'r') as b:
			test_body = b.read()
		self.assertEqual(body, ast.literal_eval(test_body))
		
		
	def message_headers(self, message, message_type):
		"""
		extracting headers given the entire message dictionary
		"""
		
		header = self.list_mails.extract_headers(message)
		with open('extractor/testing_resources/header/'+ message_type + '.json', 'r') as h:
			test_header = h.read()
		self.assertEqual.__self__.maxDiff = None
		self.assertEqual(header, ast.literal_eval(test_header))
		
		
	def test_mail_extraction(self):
		for message_type in self.message_types:
			with open('extractor/testing_resources/mail/'+ message_type + '.json', 'r') as m:
				message = ast.literal_eval(m.read())
				
			self.message_body(message, message_type)
			self.message_headers(message, message_type)
			
			
			
class CheckURLs(TestCase):
	def setUp(self):
		self.client = Client()
		settings.SESSION_ENGINE = 'django.contrib.sessions.backends.file'
		engine = import_module(settings.SESSION_ENGINE)
		store = engine.SessionStore()
		store.save()
		self.session = store
		self.client.cookies[settings.SESSION_COOKIE_NAME] = store.session_key
		
		self.user_flow = FlowModel.objects.create(flow=settings.FLOW)
		
		self.factory = RequestFactory()
		self.factory.session=self.session
	def test_unauthorised_login(self):
		"""
		User opening loggedin page without logging in
		"""
		
		response = self.client.get('/email-extractor/')
		self.assertRedirects(response, 'http://testserver/?next=/email-extractor/')
		
		
	def test_wrong_oauthcallback_credentials(self):
		"""
		If a wrong oauth-callback URL is specified due to modifications by user or due to some other factors
		"""
		
		
		session = self.session
		session['temp'] = self.user_flow.id
		session.save()
		
		response = self.client.get('/oauth2callback?code=some_wrong_code')
		self.assertTemplateUsed(response, 'homepage.html')
		self.assertContains(response, 'A problem occured wihle creating a new account. Please register again')
		
		
		
	def test_account_already_exists(self):
		"""
		If user tries to create an account with an already registered email id
		"""
		
		self.factory.session['temp']= self.user_flow.id
		oauth2callback(self.factory)