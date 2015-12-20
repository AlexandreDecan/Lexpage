# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0002_auto_20151107_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='theme',
            field=models.CharField(verbose_name='Thème', max_length=16, choices=[('style', 'Lexpage V4'), ('style_nowel', 'Nowel')], null=True, blank=True),
        ),
    ]
