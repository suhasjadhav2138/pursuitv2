# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-01-26 03:53
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0012_auto_20180116_0024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sale',
            name='date_time',
            field=models.DateTimeField(default=datetime.datetime(2018, 1, 26, 3, 53, 32, 275546)),
        ),
    ]
