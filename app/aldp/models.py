from django.db import models
from django.contrib.auth.models import User

from board.models import Message

class DatedWithMessagesAndAuthor(models.Model):
    author = models.ForeignKey(User, verbose_name='Modérateur', related_name='+')
    # TODO: définir ceci en fonction de la date du starting_message
    date_started = models.DateTimeField(verbose_name='Date de démarrage', blank=True, null=True,
                                        db_index=True)
    # TODO: définir ceci en fonction de la date du ending_message
    date_ended = models.DateTimeField(verbose_name='Date de fin', blank=True, null=True)
    starting_message = models.ForeignKey(Message, verbose_name='Message d\'annonce',
                                         related_name='+', blank=True, null=True)
    ending_message = models.ForeignKey(Message, verbose_name='Message de cloture',
                                       related_name='+', blank=True, null=True)

    class Meta:
        abstract = True

class Season(DatedWithMessagesAndAuthor):
    title = models.CharField(verbose_name='Titre', max_length=80)
    slug = models.SlugField(max_length=90)
    description = models.TextField(verbose_name='Description', help_text='Description de la saison')

class Turn(DatedWithMessagesAndAuthor):
    season = models.ForeignKey('Season', verbose_name='Saison', blank=True, null=True)
    number = models.SmallIntegerField(verbose_name='Numéro')
    # Todo: check unicity of (Season, Number)

class Question(models.Model):
    author = models.ForeignKey(User, related_name='+', verbose_name='Author', blank=True)
    turn = models.ForeignKey(Turn, verbose_name='Manche', blank=True, null=True)
    text = models.CharField(verbose_name='Texte', max_length=80, blank=True)

    @property
    def season(self):
        return self.turn.season if self.turn else None

class Subscription(models.Model):
    """
    Pseudo OneToOne through model between Season and User.
    This class is used to send appropriate notifications to the users.
    """
    season = models.ForeignKey(Season)
    user = models.ForeignKey(User, related_name='+')
