from django.contrib.auth import authenticate
import httplib2, base64
from stripogram import html2text
from oauth2client.django_orm import Storage
from apiclient.discovery import build
from oauth2client import client
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from gextracto import models
from gextracto.models import UserData
from django.core.mail import send_mail
from django.utils.functional import SimpleLazyObject
from django.core import mail
from gextracto.models import CredentialsModel
from gextracto.models import User


def extract_headers( message):
    """
        Extract the headers for a single mail and returns it
        {To, From, Subject}
    """
    
    needed_fields = ('From', 'To', 'Subject')
    return {i['name']:i['value'] for i in  message['payload']['headers'] if i['name'] in needed_fields}
        




def get_message_body( message):
    """
        Get the body of an email
        Recursively look for the body for different mimetypes
        Returns the body as text/plain
    """
    
    if 'payload' in message:
        return get_message_body(message['payload'])
    
    elif 'parts' in message:
        return get_message_body(message['parts'][0])
    
    else:
        data = base64.urlsafe_b64decode(message['body']['data'].encode('ASCII'))
        markdown_data = html2text(data)#.decode('utf-8', "replace")
        data = data.replace("\n", "<br/>")
        
        # return {markdown, html}
        return {'markdown':unicode( markdown_data,"ISO-8859-1"), 'html':unicode(data,"ISO-8859-1")} if markdown_data else {'html':unicode(data,"ISO-8859-1")}
        
        


def message_content_html( userId, message_id, service):
    """
    Make queries to get the content for a mail given its message id
    Returns all the content
    """
    
    content = {'id':message_id}
    # try
    message = service.users().messages().get(userId=userId, id=message_id).execute()
    body = get_message_body(message)
    if body == "":
        body = "<empty message>"
    headers = extract_headers(message)
    content['body'] = body
    content.update(headers)

    return content




def collect_mails( user, messages, service):
    """
    Collect the content for all the mails currently downloaded
    """
    
    all_messages = []
    try:
        for message in messages:
            content = message_content_html(user.username, message['id'], service)
            all_messages.append(content)
        return all_messages
                
    # return empty list if no messages were downloaded
    except KeyError:
        return []
    
    
def get(usern,labeln):
    print("hiii I am here")
    user = User.objects.get(username=usern)
    label_id = labeln
    storage = Storage(models.CredentialsModel, 'id', user, 'credential')
    credentials = storage.get()
    http_auth = credentials.authorize(httplib2.Http())
    service = build('gmail', 'v1', http=http_auth)
    user_Id = user.username
    
    
    # try
    # call Google API with a request to get a list of all the labels
    try:
        response = service.users().messages().list(userId=user_Id, labelIds=label_id).execute()
        all_messages = collect_mails(user, response['messages'], service)
    except:
        all_messages =[]

    if not all_messages:
        send_mail('Oops! Data Not Available', 'Hello, The Label you selected has no data.','(Gextracto) Gextracto <infowikkitech@gmail.com>',[user_Id],fail_silently=False)
        return Response([])
    else:
        print len(all_messages)
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            try:
                response = service.users().messages().list(userId=user_Id,labelIds=label_id, pageToken=page_token).execute()
                print response
                all_messages.extend(collect_mails(user, response['messages'], service))
                print len(all_messages)
            except:
                continue
        for x in range(0,len(all_messages)):
            b=all_messages[x]
            try:
                instance= UserData(user_id=user ,label=label_id, sender = b['From'] , subject=b['Subject'] , body=b['body'])
                instance.save()
                print x
            except KeyError as e:
                print e
                continue
        print all_messages        
        send_mail('Your Download Ready!', 'Hello, Your Download has been ready. kindky Login to Gmail Extractor and go to MyDownload section to download.','(Gextracto) Gextracto <infowikkitech@gmail.com>',[user_Id],fail_silently=False)
        print("hi after amial")
