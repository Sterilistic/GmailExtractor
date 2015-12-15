import httplib2, base64
from stripogram import html2text
from oauth2client.django_orm import Storage
from apiclient.discovery import build
from oauth2client import client

from django.contrib.auth.models import User
from .models import CredentialsModel
from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

try:
    import simplejson as json
except:
    import json

DOWNLOAD_LIMIT = settings.DOWNLOAD_LIMIT


class ListLables(APIView):
    """
    List all the labels just after the user has logged in
    """
    # allow this API call only if user has logged in
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        """
        Make a query using Google API to get a list of all labels
        The API returns a list of all the labels
        """
        user = request.user
        userId = user.username
        storage = Storage(CredentialsModel, 'id', user, 'credential')
        credentials = storage.get()
        http = httplib2.Http()
        http_auth = credentials.authorize(http)
        print http_auth
        service = build('gmail', 'v1', http=http)
        print service
        # try
        response = service.users().labels().list(userId=userId).execute()

        labels = [{'id': label['id'], 'name': label['name']} for label in response['labels']]
        # delete service object
        return Response(labels)


class getUser(APIView):
    # allow this API call only if user has logged in
    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        userId = user.username
        return Response(userId)


class ListMails(APIView):
    """
    Gets a list of a specified number mail ids for a particular label
    Extracts the email in the form of plain/text
    The API returns all the extracted mails
    """

    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def extract_headers(self, message):
        """
        Extract the headers for a single mail and returns it
        {To, From, Subject}
        """

        needed_fields = ('From', 'To', 'Subject')
        return {i['name']: i['value'] for i in message['payload']['headers'] if i['name'] in needed_fields}

    def get_message_body(self, message):
        """
        Get the body of an email
        Recursively look for the body for different mimetypes
        Returns the body as text/plain
        """

        if 'payload' in message:
            return self.get_message_body(message['payload'])
        elif 'parts' in message:
            return self.get_message_body(message['parts'][0])
        else:
            data = base64.urlsafe_b64decode(message['body']['data'].encode('ASCII'))
            markdown_data = html2text(data)
            data = data.replace("\n", "<br/>")

            # return {markdown, html}
            return {'markdown': unicode(markdown_data, "ISO-8859-1"), 'html': unicode(data, "ISO-8859-1")} if markdown_data else {'html': unicode(data, "ISO-8859-1")}

    def message_content_html(self, userId, message_id, service):
        """
        Make queries to get the content for a mail given its message id
        Returns all the content
        """
        content = {'id': message_id}
        # try
        message = service.users().messages().get(userId=userId, id=message_id).execute()
        mimetype = message['payload']['mimeType']
        if mimetype == 'text/html':
            return {}
        else:
            body = self.get_message_body(message)
            if body == "":
                body = "<empty message>"

        headers = self.extract_headers(message)
        content['body'] = body
        content.update(headers)

        return content

    def collect_mails(self, user, messages, service):
        """
        Collect the content for all the mails currently downloaded
        """

        all_messages = []
        try:
            for message in messages:
                content = self.message_content_html(user.username, message['id'], service)
                if content:
                    all_messages.append(content)

            return all_messages

        # return empty list if no messages were downloaded
        except KeyError:
            return []

    def get(self, request, format=None):
        """
        Handles the GET request to get all the mails for a label
        Paginages through the GAPI content if required
        API returns all the messages
        {To, From, Subject, body}
        """

        user = request.user
        storage = Storage(CredentialsModel, 'id', user, 'credential')
        credentials = storage.get()
        http_auth = credentials.authorize(httplib2.Http())
        service = build('gmail', 'v1', http=http_auth)
        user_Id = user.username
        label_id = request.GET['label']

        # try
        # call Google API with a request to get a list of all the labels
        response = service.users().messages().list(userId=user_Id, labelIds=label_id, maxResults=100).execute()
        try:
            all_messages = self.collect_mails(user, response['messages'], service)
        except:
            return Response([])

        if len(all_messages) == 0:
            return Response([])
        elif len(all_messages) >= DOWNLOAD_LIMIT:
            return Response(all_messages[0: DOWNLOAD_LIMIT - 1])
        else:
            if 'nextPageToken' in response:
                page_token_flag = True

            # request more more mails if the download limit has not yet been satisfied
                while(page_token_flag and len(all_messages) < DOWNLOAD_LIMIT):
                    response = service.users().messages().list(userId=user_Id, labelIds=label_id, pageToken=response['nextPageToken'], maxResults=100).execute()
                    try:
                        all_messages.append(self.collect_mails(response['messages']))
                    except:
                        pass
                    if len(all_messages) >= DOWNLOAD_LIMIT:
                        return Response(all_messages[0: DOWNLOAD_LIMIT - 1])

                # check for presence of nextPageToken in response
                    page_token_flag = 'nextPageToken' in response

            return Response(all_messages)

