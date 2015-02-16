# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogBoardLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post', models.OneToOneField(to='blog.BlogPost')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Flag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': 'Suivi',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(help_text='Mis en page avec le BBCode.', verbose_name='Message')),
                ('moderated', models.BooleanField(default=False, help_text='Si le message est mod\xe9r\xe9, son auteur ne pourra plus le modifier.', verbose_name='Message mod\xe9r\xe9 ?')),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('author', models.ForeignKey(related_name='board_post', verbose_name='Auteur', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date'],
                'get_latest_by': 'date',
                'verbose_name': 'Message',
                'permissions': (('can_moderate', 'Peut mod\xe9rer'), ('can_destroy', 'Peut d\xe9truire')),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MessageHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True, verbose_name='Date')),
                ('text', models.TextField(verbose_name='Historique')),
                ('edited_by', models.ForeignKey(related_name='+', verbose_name='Auteur de la modification', to=settings.AUTH_USER_MODEL)),
                ('message', models.ForeignKey(related_name='history', verbose_name='Message', to='board.Message')),
            ],
            options={
                'ordering': ['date'],
                'get_latest_by': 'date',
                'verbose_name': '\xc9dition de message',
                'verbose_name_plural': '\xc9ditions de message',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=80, verbose_name='Titre')),
                ('slug', models.SlugField(max_length=90)),
                ('number', models.IntegerField(default=0, verbose_name='Nombre de messages')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date de cr\xe9ation')),
                ('last_message', models.ForeignKey(related_name='+', default=-1, verbose_name='Dernier message', to='board.Message')),
            ],
            options={
                'ordering': ['date_created'],
                'get_latest_by': 'date_created',
                'verbose_name': 'Discussion',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='message',
            name='thread',
            field=models.ForeignKey(verbose_name='Sujet', to='board.Thread'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flag',
            name='message',
            field=models.ForeignKey(verbose_name='Dernier message lu', to='board.Message'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flag',
            name='thread',
            field=models.ForeignKey(verbose_name='Sujet', to='board.Thread'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flag',
            name='user',
            field=models.ForeignKey(related_name='+', verbose_name='Auteur', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='flag',
            unique_together=set([('user', 'thread')]),
        ),
        migrations.AddField(
            model_name='blogboardlink',
            name='thread',
            field=models.OneToOneField(to='board.Thread'),
            preserve_default=True,
        ),
    ]
