# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-11-29 12:23
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0007_auto_20171129_1215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search_credits',
            name='free_credits_used',
            field=models.CharField(default=0, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='search_credits',
            name='paid_credits_used',
            field=models.CharField(default=0, max_length=2, null=True),
        ),
        migrations.AlterField(
            model_name='search_details',
            name='date_pulled',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2017, 11, 29, 12, 23, 2, 976525)),
        ),
    ]
