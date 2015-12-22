# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='thread',
            name='last_message',
            field=models.ForeignKey(verbose_name='Dernier message', related_name='+', to='messaging.Message', default=-1, db_constraint=False),
        ),
    ]
