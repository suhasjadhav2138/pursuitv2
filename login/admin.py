# -*- coding: utf-8 -*-
from .models import UserProfilename, Document, Search_details, OutputDocument
from django.contrib import admin


class Search_detailsAdmin(admin.ModelAdmin):
    meta = Search_details
    list_display = (
        'user', 'run_id', 'first_name', 'last_name', 'date_pulled', 'name', 'company_url', 'email_guess',
        'email_score',)


admin.site.register(UserProfilename)
admin.site.register(Document)
admin.site.register(Search_details, Search_detailsAdmin)
admin.site.register(OutputDocument)

# admin.site.register(UserSession, UserSessionAdmin)
