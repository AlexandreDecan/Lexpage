# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Slogan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.CharField(max_length=50, verbose_name='Auteur')),
                ('slogan', models.TextField(verbose_name='Slogan')),
                ('date', models.DateField(auto_now_add=True, verbose_name="Date d'ajout")),
                ('is_visible', models.BooleanField(default=False, verbose_name='Visible ?')),
            ],
            options={
                'permissions': (('can_set_visible', 'Peut rendre visible'),),
            },
            bases=(models.Model,),
        ),
    ]
