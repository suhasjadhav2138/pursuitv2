# -*- coding: utf-8 -*-
from .models import UserProfilename, Document, Search_details, OutputDocument, Search_credits, Track_guest_details
from django.contrib import admin
# from django.contrib.sessions.models import Session


class Search_detailsAdmin(admin.ModelAdmin):
    meta = Search_details
    list_display = (
        'user', 'run_id', 'first_name', 'last_name', 'date_pulled', 'name', 'company_url', 'email_guess',
        'email_score',)


class Search_creditsAdmin(admin.ModelAdmin):
    meta = Search_credits
    list_display = ('user', 'free_credits_used', 'paid_credits_used',)

class Track_userAdmin(admin.ModelAdmin):
    meta = Track_guest_details
    list_display = ('user', 'ip_address', 'mac_address',)
#
# class SessionAdmin(admin.ModelAdmin):
#     def _session_data(self, obj):
#         return obj.get_decoded()
#
#     list_display = ['session_key', '_session_data', 'expire_date']


# admin.site.register(Session, SessionAdmin)
admin.site.register(UserProfilename)
admin.site.register(Document)
admin.site.register(Search_details, Search_detailsAdmin)
admin.site.register(OutputDocument)
admin.site.register(Search_credits, Search_creditsAdmin)
admin.site.register(Track_guest_details, Track_userAdmin)


# admin.site.register(UserSession, UserSessionAdmin)
