# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-22 13:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyzer', '0004_auto_20170222_0906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='url_rpt',
            field=models.CharField(default=b'na', max_length=200),
        ),
        migrations.AlterField(
            model_name='result',
            name='result',
            field=models.CharField(blank=True, default=b'na', max_length=200),
        ),
    ]