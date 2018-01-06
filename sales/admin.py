# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from sales.models import Sale
from django.contrib import admin
class SalesAdmin(admin.ModelAdmin):
    meta = Sale
    list_display = (
        'charge_id', 'user_name', 'email_id', 'amount', 'emails_count', 'emails_balance_count', 'date_time',)

# Register your models here.
admin.site.register(Sale, SalesAdmin)

