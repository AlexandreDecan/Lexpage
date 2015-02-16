# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='Message')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('author', models.ForeignKey(related_name='+', verbose_name='Auteur', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
                'get_latest_by': 'date',
                'verbose_name': 'Message',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageBox',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_read', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0), verbose_name='Derni\xe8re lecture')),
                ('is_starred', models.BooleanField(default=False, verbose_name='Favorites ?')),
                ('status', models.SmallIntegerField(default=1, verbose_name='\xc9tat', choices=[(1, 'Normal'), (2, 'Archiv\xe9e'), (-1, 'Supprim\xe9e')])),
            ],
            options={
                'ordering': ['-thread__last_message__date'],
                'verbose_name': 'Bo\xeete de r\xe9ception',
                'verbose_name_plural': 'Bo\xeetes de r\xe9ceptions',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=60, verbose_name='Titre')),
                ('last_message', models.ForeignKey(related_name='+', default=-1, verbose_name='Dernier message', to='messaging.Message')),
            ],
            options={
                'ordering': ['-last_message__date'],
                'get_latest_by': 'last_message',
                'verbose_name': 'Conversation',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='messagebox',
            name='thread',
            field=models.ForeignKey(verbose_name='Conversation', to='messaging.Thread'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='messagebox',
            name='user',
            field=models.ForeignKey(verbose_name='Propri\xe9taire', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(verbose_name='Conversation', to='messaging.Thread'),
            preserve_default=True,
        ),
    ]
