# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-21 14:20
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interpreter', '0004_requestfly_responsefly'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='requestfly',
            options={'ordering': ('url_analyzer',)},
        ),
        migrations.AlterModelOptions(
            name='responsefly',
            options={'ordering': ('query',)},
        ),
    ]
