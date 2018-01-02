from __future__ import unicode_literals
import json
from django.http import HttpRequest

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
from Controller import validate_email
from django.contrib.auth.decorators import login_required
from django.core.files import File
from os.path import join
from django.conf import settings


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
        full_name = first_name + " " + last_name
        ip_data = get_ip_location()
        ip_data["ip"] = request.META.get('REMOTE_ADDR')
        track_user = Track_guest_details.objects.all()
        data_tracked = []
        for i in track_user:
            if (ip_data["ip"] == i.ip_address):
                data_tracked.append(i.mac_address)
            else:
                data_tracked = []

        print track_user, "MMMMMMMMMMMMMMMMMMMMMMM"

        if data_tracked == []:
            client_address = request.META.get('HTTP_X_FORWARDED_FOR')
            print request.META.get('REMOTE_ADDR'),"zzzzzzzzzzzzzzzzzzzzzzzzzzz"
            print client_address,"yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
            track_update = Track_guest_details(user="guest", ip_address=request.META.get('REMOTE_ADDR'), mac_address=ip_data["mac"])
            track_update.save()

            print track_user, "uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu"
            # fetch = Search_details.objects.filter(name = full_name)
            # for i in fetch:
            #     if i.name == full_name:
            #         print "ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo"
            print full_name, "pppppppppppppp"
            # print fetch,"iiiiiiiiiiiiiiiiii"

            print ip_data
            user = "Guest"

            person_details = validate_email.select_type(user, data_list)

            # person_details = dict(person_details)
            # print person_details
            # # if request.user == None:
            # print person_details
            # user = "Guest"
            # if person_details[0]["email_score"] > 95:
            #     data_update = Search_details(user=user, run_id=002, date_pulled=datetime.now(),
            #                                  first_name=person_details[0]['first_name'],
            #                                  last_name=person_details[0]["last_name"],
            #                                  name=person_details[0]["name"],
            #                                  company_url=person_details[0]["company_url"],
            #                                  email_guess=person_details[0]["email_guess"],
            #                                  email_score=person_details[0]["email_score"], )
            #     data_update.save()
            search_message = "Search Results"
            message = ""
            try:
                message = """<a href="/accounts/register"/>Sign Up</a> to get more 19 free credits"""
                person_details = person_details[0]['email_guess']
            except:
                person_details = "domain not found"

            print message
            print person_details
            return render(request, 'login/index.html',
                          {'details': person_details, 'search': search_message, 'msg': message})
        else:
            message = """You have used your Only free search, Kindly <a href="/accounts/register"/>Sign Up</a> to get more 19 free credits"""

            return render(request, "login/index.html", {'msg': message})

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
                request.session['userid'] = user.id

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
    # del request.session['userid']

    return render(request, "login/index.html", {})


# profile page for the users
# def profile_view(request):


#     return render(request, 'login/profile.html', {})

# upload csv and read in construction
@login_required()
def validate_view(request):
    if request.method == 'GET':
        form = DocumentForm()
        # person_data = Search_details.objects.filter(user=request.user)
        # for i in person_data:
        #     print i.first_name, "]]]]]]]]]]]]]]]]]]"
        # 'details': person_data
        return render(request, "login/profile.html", {'form': form})

    if request.method == 'POST' and not request.FILES:
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        title = 'CEO'
        # company_email = request.POST.get('company_email')
        company_website = request.POST.get('company_website')

        print first_name, last_name, title, company_website
        data_list = [first_name, last_name, title, company_website]
        print data_list
        name_search = first_name + " " + last_name
        filter_records = Search_details.objects.filter(user=request.user).values()
        print filter_records, ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        for i in filter_records:
            if (i["name"] == name_search) and (i["company_url"] == company_website):
                print i

                search_message = "Search Results"
                try:

                    person_details = i['email_guess']
                except:
                    person_details = "domain not found"
                # person_details = person_details[0]
                # person_data = Search_details.objects.filter(user=request.user)
                print person_details, "oooooooooooooooooooooooooooooo"
                form = DocumentForm()

                return render(request, 'login/profile.html',
                              {'details': person_details, 'form': form, "search": search_message})




        # search_in_db = Search_details.objects.file
        # person_details = dict(person_details)
        # if request.user == None:
        user = request.user
        # if user in

        read_credits = Search_credits.objects.filter(user=user).count()
        print read_credits
        if read_credits == 0:
            print "insideeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

            credits_add = Search_credits(user=user, free_credits_used=1, paid_credits_used=0)
            credits_add.save()

        else:
            if int(Search_credits.objects.get(user=user).free_credits_used) <= 20:
                print read_credits, "iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii"
                credits_update = Search_credits.objects.get(user=user)
                credits_update.free_credits_used = (int(credits_update.free_credits_used) + 1)
                credits_update.save()
                print (credits_update.free_credits_used)

            else:
                notify = "Kindly Buy membership to increase credits and enable Upload csv option"
                return render(request, 'login/profile.html',
                              {'search': notify})


                # credits_update = Search_credits(user=user, free_credits_used = )
                # ------------------------------------------------test---------------------------------------
        person_details = validate_email.select_type(request.user, data_list)

        # if person_details[0]["email_score"] > 95:
        #     data_update = Search_details(user=user, run_id=002, date_pulled=datetime.now(),
        #                                  first_name=person_details[0]['first_name'],
        #                                  last_name=person_details[0]["last_name"],
        #                                  name=person_details[0]["name"],
        #                                  company_url=person_details[0]["company_url"],
        #                                  email_guess=person_details[0]["email_guess"],
        #                                  email_score=person_details[0]["email_score"])
        #     data_update.save()
        search_message = "Search Results"
        try:

            person_details = person_details[0]['email_guess']
        except:
            person_details = "domain not found"
        # person_details = person_details[0]
        # person_data = Search_details.objects.filter(user=request.user)
        print person_details, "oooooooooooooooooooooooooooooo"
        form = DocumentForm()

        return render(request, 'login/profile.html',
                      {'details': person_details, 'form': form, "search": search_message})
    else:
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            newdoc = Document(docfile=request.FILES['docfile'], user=request.user)
            print newdoc, "ooooooooooooooooooooooooooooooooooooooo"

            newdoc.save()
            # -----------------------------------
            path = 'media/' + str(newdoc)
            print path
            read_credits = Search_credits.objects.filter(user=request.user).count()
            print read_credits
            if read_credits == 0:
                processed_data = validate_email.run(path, request.user, process_count=1)

                print "insideeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"

                credits_add = Search_credits(user=request.user, free_credits_used=len(processed_data),
                                             paid_credits_used=0)
                credits_add.save()

            else:

                if int(Search_credits.objects.get(user=request.user).free_credits_used) <= 20:
                    processed_data = validate_email.run(path, request.user, process_count=1)

                    print read_credits, "8888888888888889999999999999999999999999999999777777777"
                    credits_update = Search_credits.objects.get(user=request.user)
                    credits_update.free_credits_used = (int(credits_update.free_credits_used) + len(processed_data))
                    credits_update.save()
                    print (credits_update.free_credits_used)

                else:
                    notify = "You don't have enough credits kindly buy new plan and try again"
                    return render(request, 'login/profile.html',
                                  {'details': notify})

                    # print processed_data
                    # for i in processed_data:
                    #     print i
                    # for i in processed_data:
                    #     if i["email_score"] > 95:
                    #         data_updates = Search_details(user=request.user, run_id=002, date_pulled=datetime.now(),
                    #                                       first_name=i['first_name'],
                    #                                       last_name=i['last_name'],
                    #                                       name=i['name'], company_url=i['company_url'],
                    #                                       email_guess=i['email_guess'],
                    #                                       email_score=i['email_score'])
                    #         data_updates.save()
                    # ------------------------------------
            path = "media/outputFile/"
            print path
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


# @login_required
# def list_file(request):
#     # Handle file upload
#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             newdoc = Document(docfile=request.FILES['docfile'], user=request.user)
#             newdoc.save()
#             print request.FILES['docfile']
#
#             documents = Document.objects.all()
#
#
#             # Redirect to the document list after POST
#             return render(request, 'login/profile.html', {'documents': documents})
#
#     else:
#         form = DocumentForm()  # A empty, unbound form
#
#     # Load documents for the list page
#     documents = Document.objects.all()
#
#     # Render list page with the documents and the form
#     return render(
#         request,
#         'login/profile.html',
#         {'documents': documents, 'form': form}
#     )

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
