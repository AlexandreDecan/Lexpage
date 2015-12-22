# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0003_profile_theme'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='theme',
            field=models.CharField(verbose_name='Thème', null=True, blank=True, max_length=16, choices=[('style', 'Lexpage'), ('style_nowel', 'Nowel')], help_text='Laissez vide pour adopter automatiquement le thème du moment.'),
        ),
    ]
