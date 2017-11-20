from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib.sessions.models import Session
from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.contrib.gis.geoip2 import GeoIP2
import re
import json
from urllib2 import urlopen
from django.contrib import admin

class UserProfilename(models.Model):
    name = models.OneToOneField(User, primary_key=True)
    email = models.EmailField(max_length=50)
    contact = models.CharField(max_length=20)
    skill = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Document(models.Model):
    user = models.ForeignKey(User, null=True, blank=True)
    docfile = models.FileField(upload_to='documents/%Y/%m/%d')
    def __unicode__(self):
        return unicode(self.docfile)


class Search_details(models.Model):
    user = models.CharField( max_length=100, null=True, blank=True)
    run_id = models.CharField(max_length=100)
    date_pulled = models.DateTimeField(default=datetime.now(), blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    # email_original = models.EmailField(max_length=30)
    company_url = models.CharField(max_length=100)
    email_guess = models.CharField(max_length=100)
    email_score = models.CharField(max_length=100)

# class UserSession(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL)
#     session = models.ForeignKey(Session)
#     ip = models.CharField(max_length=25) 
#     location = models.CharField(max_length=100) 
    
    # def __unicode__(self):
    #     return unicode(self.sessio)
    

        # def user_logged_in_handler(sender, request, user, **kwargs):
        #     print("ooooooooooooooooooooooooooooooooooooooooooooooooo")
        #     data= get_ip_location()
        #     ip = data['ip']
        #     location = data['city']+', '+data['region'] + ', '+ data['country']
        #     UserSession.objects.get_or_create(
        #         user = user,
        #         session_id = request.session.session_key,
        #         ip=ip,
        #         location=location
        #     )

        # user_logged_in.connect(user_logged_in_handler)

def get_ip_location():
    url = 'http://ipinfo.io/json'
    response = urlopen(url)
    data_dict = json.load(response)
    return data_dict
    # IP=data['ip']
    # org=data['org']
    # city = data['city']
    # country=data['country']
    # region=data['region']


