# -*- coding: utf-8 -*-
from .models import UserProfilename, Document, Search_details, OutputDocument, Search_credits
from django.contrib import admin


class Search_detailsAdmin(admin.ModelAdmin):
    meta = Search_details
    list_display = (
        'user', 'run_id', 'first_name', 'last_name', 'date_pulled', 'name', 'company_url', 'email_guess',
        'email_score',)


class Search_creditsAdmin(admin.ModelAdmin):
    meta = Search_credits
    list_display = ('user', 'free_credits_used', 'paid_credits_used',)


admin.site.register(UserProfilename)
admin.site.register(Document)
admin.site.register(Search_details, Search_detailsAdmin)
admin.site.register(OutputDocument)
admin.site.register(Search_credits, Search_creditsAdmin)

# admin.site.register(UserSession, UserSessionAdmin)
