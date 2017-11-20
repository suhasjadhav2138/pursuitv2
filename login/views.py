from __future__ import unicode_literals
import json
from .form import UserLoginForm, UserRegisterForm, DocumentForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.template import RequestContext, loader
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from .models import UserProfilename, Document
from datetime import datetime
import csv
from django.core.urlresolvers import reverse
from models import Search_details
from Controller import validate_email
from django.contrib.auth.decorators import login_required


# home page of the website
def index_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        title = 'CEO'
        # company_email = request.POST.get('company_email')
        company_website = request.POST.get('company_website')

        print first_name, last_name, title, company_website
        data_list = [first_name, last_name, title, company_website]
        print data_list
        person_details = validate_email.select_type(data_list)
        # person_details = dict(person_details)
        print person_details
        # if request.user == None:
        user = "Guest"
        data_update = Search_details(user=user, run_id=002, date_pulled=datetime.now(),
                                     first_name=person_details[0]['first_name'], last_name=person_details[0]["last_name"],
                                     name=person_details[0]["name"], company_url=person_details[0]["company_url"],
                                     email_guess=person_details[0]["email_guess"],
                                     email_score=person_details[0]["email_score"])
        data_update.save()
        try:

            person_details = person_details[0]['email_guess']
        except:
            person_details = "domain not found"
        return render(request, 'login/index.html', {'details': person_details})
    if request.method == 'GET':
        return render(request, "login/index.html", {})


# login page

def login_view(request):
    print "inside login viewwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww "
    print request.POST
    if request.method == "POST":
        username = request.POST['username']
        print username
        password = request.POST['password']
        print username, password, "username and password"
        user = authenticate(username=username, password=password)
        form = User(request.POST)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/profile/')
            else:
                return render(request, 'login/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'login/login.html', {'error_message': 'Enter correct username or password'})
    return render(request, "login/login.html", {})


# registration page
@csrf_exempt
def register_view(request):
    title = "Register"
    form = UserRegisterForm(request.POST)
    print form
    if form.is_valid():
        user = form.save(commit=False)
        email = form.cleaned_data.get('email')
        usern = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user.set_password(password)
        authenticate(username=user.username, password=password)
        user.is_active = True
        user.save()
        return HttpResponseRedirect('/accounts/login/')

    context = {
        "form": form,
        "title": title
    }
    return render(request, "login/registration.html", context)


# logout user from his profile to the homePage
def logout_view(request):
    logout(request)
    return render(request, "login/index.html", {})


# profile page for the users
# def profile_view(request):


#     return render(request, 'login/profile.html', {})

# upload csv and read in construction

def validate_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        title = 'CEO'
        # company_email = request.POST.get('company_email')
        company_website = request.POST.get('company_website')

        print first_name, last_name, title, company_website
        data_list = [first_name, last_name, title, company_website]
        print data_list
        person_details = validate_email.select_type(data_list)
        # person_details = dict(person_details)
        print person_details
        # if request.user == None:
        user = request.user
        data_update = Search_details(user=user, run_id=002, date_pulled=datetime.now(),
                                     first_name=person_details[0]['first_name'], last_name=person_details[0]["last_name"],
                                     name=person_details[0]["name"], company_url=person_details[0]["company_url"],
                                     email_guess=person_details[0]["email_guess"],
                                     email_score=person_details[0]["email_score"])
        data_update.save()
        try:

            person_details = person_details[0]['email_guess']
        except:
            person_details = "domain not found"
        return render(request, 'login/index.html', {'details': person_details})
    if request.method == 'GET':
        return render(request, "login/index.html", {})


@login_required
def list_file(request):
    # Handle file upload
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], user=request.user)
            newdoc.save()
            print request.FILES['docfile']

            documents = Document.objects.all()


            # Redirect to the document list after POST
            return render(request, 'login/profile.html', {'documents': documents})

    else:
        form = DocumentForm()  # A empty, unbound form

    # Load documents for the list page
    documents = Document.objects.all()

    # Render list page with the documents and the form
    return render(
        request,
        'login/profile.html',
        {'documents': documents, 'form': form}
    )

# def email_validate(request):
#     print("jsdhgfsjhdfgsjhfgsdjhfgjhfgsdjhfgsdjfgsdjhfgsdjhfg")
#     if request.method == 'POST':
#         first_name= request.POST.get('first_name')
#         last_name= request.POST.get('last_name')
#         title= 'CEO'
#         company_email = request.POST.get('company_email')
#         company_website= request.POST.get('company_website')

#         print first_name,last_name,title,company_email,company_website
#         data_list = [first_name,last_name,title,company_email,company_website]
#         print data_list
#         person_details = validate_email.select_type(data_list)
#         print person_details
#         return render(request, 'login/index.html', {'details': person_details})
