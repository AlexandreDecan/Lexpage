from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100, verbose_name='Titre')),
                ('slug', models.SlugField(max_length=120)),
                ('tags', models.CharField(help_text='\xc9tiquettes associ\xe9es, s\xe9par\xe9es par un espace.', max_length=100, verbose_name='\xc9tiquettes', blank=True)),
                ('abstract', models.TextField(help_text='Mis en page avec Markdown.', verbose_name='Chapeau')),
                ('text', models.TextField(help_text='Mis en page avec Markdown.', verbose_name='Contenu', blank=True)),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='Date de cr\xe9ation')),
                ('date_approved', models.DateTimeField(null=True, verbose_name='Date de validation', blank=True)),
                ('date_published', models.DateTimeField(null=True, verbose_name='Date de publication', blank=True)),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='Date de derni\xe8re modification', null=True)),
                ('priority', models.SmallIntegerField(default=5, verbose_name='Priorit\xe9', choices=[(1, 'Urgente'), (2, 'Haute'), (5, 'Normale'), (8, 'Faible'), (14, 'Tr\xe8s faible')])),
                ('status', models.SmallIntegerField(default=1, verbose_name='\xc9tat', choices=[(1, 'Brouillon'), (2, 'Propos\xe9'), (3, 'Valid\xe9'), (4, 'Publi\xe9'), (5, 'Masqu\xe9')])),
                ('approved_by', models.ForeignKey(related_name='+', verbose_name='Validateur', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)),
                ('author', models.ForeignKey(verbose_name='Auteur', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-date_published'],
                'get_latest_by': 'date_published',
                'verbose_name': 'Billet',
                'permissions': (('can_approve', 'Peut valider'),),
            },
            bases=(models.Model,),
        ),
    ]
