# Generated by Django 2.0 on 2017-12-06 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profile', '0001_squashed_0005_auto_20170408_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='theme',
            field=models.CharField(blank=True, choices=[('style', 'Lexpage'), ('style_nowel', 'Nowel'), ('style_st_patrick', 'Saint-Patrick'), ('style_halloween', 'Halloween')], help_text='Laissez vide pour adopter automatiquement le thème du moment.', max_length=16, null=True, verbose_name='Thème'),
        ),
    ]
