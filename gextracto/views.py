import httplib2
from oauth2client.django_orm import Storage
from apiclient.discovery import build
from oauth2client import client
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import logout, authenticate, login
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.db import IntegrityError
from .models import CredentialsModel, FlowModel


def user_login(request):
    """
    Login a user using email-password combination
    """
    # initiate login process if POST request is present
    if request.method == 'POST':
        username = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/email-extractor/')
            else:
                return render(request, 'homepage.html', {'Error': 'This account does not exist. Please contact the adinistrator for more details.'})
        else:
            return render(request, 'homepage.html', {'Error': 'Invalid username or password'})
    # redirect to home page if no credentials are passed with the request
    # i.e. if someone explicitly enters the URL to browser
    else:
        return redirect('/')


@login_required
def email_extractor(request):
    """
    This is the main application interface.
    All API calls are done from withing the page using JavaScript
    """
    return render(request, 'extractor.html')


def home(request):
    """
    The main homepage of the application
    This also contains the login form
    """
    if not request.user.is_authenticated():
        return render(request, 'homepage.html')

    # Redirect to the main application interface if the user is already logged in
    else:
        return redirect('/email-extractor/')


def signup(request):
    """
    Either initiates the authentication flow or stores the new user's crednetials
    """
    # Store user credentials if POST request is sent
    if request.method == 'POST':
        email_id = request.POST.get('email', '')
        password = request.POST.get('password', '')
        user = User.objects.get(username = email_id)
        user.set_password(password)
        user.is_active = True
        user.save()
        user = authenticate(username = email_id, password = password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/email-extractor/')
            else:
                return HttpResponse('disabled account')
        else:
            return HttpResponse('invalid login')
    # if credentials are not sent as a POST request, then begin authentication
    # process using Google API
    else:
        user_flow = FlowModel.objects.create(flow=settings.FLOW)
        # set a temp variable to the session containing the user id
        request.session['temp'] = user_flow.id
        auth_uri = settings.FLOW.step1_get_authorize_url()
        return redirect(auth_uri)


@csrf_protect
def oauth2callback(request):
    """
    Handles the callback request from Google
    """
    # select the flow object corresponding to the value of temp variable
    # which will be the user's id in database
    flow_object = FlowModel.objects.get(id = request.session['temp'])
    user_flow = flow_object.flow
    # get the 'code' sent by Google
    auth_code = request.GET.get('code', '')
    try:
        credentials = user_flow.step2_exchange(auth_code)
    # handle any errors in the auth code incase user tries to modify it explicitly
    except client.FlowExchangeError:
        return render(request, "homepage.html", {"Error": "A problem occured wihle creating a new account. Please register again"})
    http_auth = credentials.authorize(httplib2.Http())
    # build the API service object. All Google API calls will be made using this
    service = build('gmail', 'v1', http=http_auth)
    try:
        response = service.users().getProfile(userId='me').execute()
    except httplib2.BadStatusLine:
        # return to homepage with error message incase authentication flow was interrupted
        # by connection problems
        flow_object.delete()
        return render(request, "homepage.html", {"Error": "A problem occured wihle creating a new account. Please register again"})
    # create new user only if the user has not registered earlier
    if not User.objects.filter(username=response['emailAddress']).exists():
        user = User.objects.create_user(response['emailAddress'])
        # user entry in database should be inactive until proper credentials are provided later
        user.is_active = False
        user.save()
        storage = Storage(CredentialsModel, 'id', user, 'credential')
        storage.put(credentials)
        flow_object.delete()
        return render(request, 'signup.html', {'email_id': response['emailAddress']})
    # send an error message if an account with this email id already exists
    return render(request, "homepage.html", {"Error": "You have already created an account with this email id. Please login using your credentials"})


def loggingout(request):
    """
    Logout the user session
    """
    logout(request)
    # redirect to home page after logging out
    return redirect('/')

