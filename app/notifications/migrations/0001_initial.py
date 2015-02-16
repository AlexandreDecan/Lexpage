# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Titre')),
                ('description', models.CharField(max_length=255, verbose_name='Description', blank=True)),
                ('action', models.CharField(max_length=255, verbose_name='Action', blank=True)),
                ('app', models.CharField(max_length=50, verbose_name='Application')),
                ('key', models.CharField(max_length=100, verbose_name='Cl\xe9')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('recipient', models.ForeignKey(verbose_name='Destinataire', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
                'get_latest_by': 'date',
            },
            bases=(models.Model,),
        ),
    ]
