from __future__ import unicode_literals
import json
from website.settings import MEDIA_ROOT
from .form import UserLoginForm, UserRegisterForm, DocumentForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.template import RequestContext, loader
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from .models import UserProfilename, Document, OutputDocument, get_ip_location, Track_guest_details
from datetime import datetime
import csv
from django.core.urlresolvers import reverse
from models import Search_details, Search_credits
from sales.models import Sale
from Controller import validate_email
from django.contrib.auth.decorators import login_required
from django.core.files import File
from os.path import join
from django.conf import settings
from sales.models import Sale

import datetime
# home page of the website
def index_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        title = 'CEO'
        # company_email = request.POST.get('company_email')
        company_website = request.POST.get('company_website')


        data_list = [first_name, last_name, title, company_website]

        full_name = first_name + " " + last_name
        ip_data = get_ip_location()
        track_user = Track_guest_details.objects.all()
        data_tracked = []
        ip_data["ip"] = request.META["REMOTE_ADDR"]

        for i in track_user:
            if (ip_data["ip"] == i.ip_address):
                data_tracked.append(i.mac_address)
            else:
                data_tracked = []



        if data_tracked == []:
            # client_address = request.META['HTTP_X_FORWARDED_FOR']

            track_update = Track_guest_details(user="guest", ip_address=request.META['REMOTE_ADDR'], mac_address=ip_data["mac"])
            track_update.save()



            user = "Guest"

            person_details = validate_email.select_type(user, data_list)

         
            message = ""
            try:
                message = """<a href="/accounts/register"/>Sign Up</a> to get more 19 free credits"""
                person_details = person_details[0]['email_guess']
            except:
                person_details = "domain not found"

           
          
            return render(request, 'login/index.html',
                          {'details': person_details, 'msg': message})
        else:
            message = """Please sign up for more email credits"""

            return render(request, "login/index.html", {'msg': message})

    if request.method == 'GET':
        return render(request, "login/index.html", {})


# login page

def login_view(request):
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
                request.session['userid'] = user.id
                user_data = Sale.objects.filter(user_name=user).values()
		if user_data:
               	    return HttpResponseRedirect('/profile/')
		else:
		    return HttpResponseRedirect('/sale/payment/')
            else:
                return render(request, 'login/login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'login/login.html', {'error_message': 'Enter correct username or password'})
    return render(request, "login/login.html", {})


# registration page
@csrf_exempt

def register_view(request):
    title = "Register"
    if request.method == "POST":

        form = UserRegisterForm(request.POST)
        print "oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
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

	else:
            return render(request, "login/registration.html", {"form":form})

           # form = UserRegisterForm()
           # context = {
            #    "form": form,
             #   "title": title,
              #  "message":"Please fill All the details"
           # }
            return render(request, "login/registration.html")
    else:
        form = UserRegisterForm()
        context = {
            "form": form,
            "title": title
        }
        return render(request, "login/registration.html", context)

    return render(request, "login/registration.html")


# logout user from his profile to the homePage
def logout_view(request):
    logout(request)
 

    return render(request, "login/index.html", {})


#load csv and read in construction
@login_required()
def validate_view(request):
    if request.method == 'GET':
        form = DocumentForm()
 
        return render(request, "login/profile.html", {'form': form})

    if request.method == 'POST' and not request.FILES:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        title = 'CEO'
        
        company_website = request.POST.get('company_website')

 
        data_list = [first_name, last_name, title, company_website]
        name_search = first_name + " " + last_name
        filter_records = Search_details.objects.filter(user=request.user).values()
 
        for i in filter_records:
            if (i["name"] == name_search) and (i["company_url"] == company_website):
        

                
                try:

                    person_details = i['email_guess']
                except:
                    person_details = "domain not found"
                
                
                form = DocumentForm()

                return render(request, 'login/profile.html',
                              {'details': person_details, 'form': form})




        
        user = request.user
        # if user in

        read_credits = Search_credits.objects.filter(user=user).count()
        if read_credits == 0:
        

            credits_add = Search_credits(user=user, free_credits_used=1, paid_credits_used=0)
            credits_add.save()

        else:
            if int(Search_credits.objects.get(user=user).free_credits_used) <= 20:
        
                credits_update = Search_credits.objects.get(user=user)
                credits_update.free_credits_used = (int(credits_update.free_credits_used) + 1)
                credits_update.save()
        
            else:
                notify = "Kindly Buy membership to increase credits and enable Upload csv option"
                return render(request, 'login/profile.html',
                              {'search': notify})


        person_details = validate_email.select_type(request.user, data_list)

        
        
        try:

            person_details = person_details[0]['email_guess']
        except:
            person_details = "domain not found"
        
        
        form = DocumentForm()

        return render(request, 'login/profile.html',
                      {'details': person_details, 'form': form})
    else:

        form = DocumentForm(request.POST, request.FILES)
        user_pay = Sale.objects.filter(user_name=request.user).count()
        
        if user_pay:
            if form.is_valid():
                newdoc = Document(docfile=request.FILES['docfile'], user=request.user)
        

                newdoc.save()
                # -----------------------------------
                path = 'media/' + str(newdoc)
        
                read_credits = Search_credits.objects.filter(user=request.user).count()
        
                if read_credits == 0:
                    processed_data = validate_email.run(path, request.user, process_count=1)

        

                    credits_add = Search_credits(user=request.user, free_credits_used=len(processed_data),
                                                 paid_credits_used=0)
                    credits_add.save()

                else:

                    if int(Search_credits.objects.get(user=request.user).free_credits_used) <= 20:
                        processed_data = validate_email.run(path, request.user, process_count=1)

        
                        credits_update = Search_credits.objects.get(user=request.user)
                        credits_update.free_credits_used = (int(credits_update.free_credits_used) + len(processed_data))
                        credits_update.save()
        
                    else:
                        notify = "You don't have enough credits kindly buy new plan and try again"
                        return render(request, 'login/profile.html',
                                      {'details': notify})

                path = "media/outputFile/"
        
                keys = processed_data[0].keys()
                with open(path + str(request.user) + "_output.csv", 'wb') as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(processed_data)
                    outfile = OutputDocument(user=request.user,
                                             output_file="outputFile/" + str(request.user) + "_output.csv")
                    outfile.save()

                documents = OutputDocument.objects.filter(user=request.user).order_by('-id')[0]

                form = DocumentForm()

                return render(request, 'login/profile.html',
                              {'data': processed_data, 'documents': documents, 'form': form})

            else:
                form = DocumentForm()


                # Redirect to the document list after POST
                return render(request, 'login/profile.html', {'form': form})
        else:
           form = DocumentForm()
           return render(request, 'login/profile.html', {'form': form})
