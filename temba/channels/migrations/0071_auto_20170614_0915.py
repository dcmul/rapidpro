# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-14 09:15
from __future__ import absolute_import, division, print_function, unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('channels', '0070_auto_20170428_1135'),
    ]

    operations = [
        migrations.AlterField(
            model_name='channelcount',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
