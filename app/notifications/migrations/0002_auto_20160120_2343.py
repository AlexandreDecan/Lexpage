# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-20 23:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='notification',
            unique_together=set([('app', 'key', 'recipient')]),
        ),
    ]
