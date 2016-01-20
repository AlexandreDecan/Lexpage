from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from board.models import Message

class DatestampedWithMessagesAndAuthor(models.Model):
    author = models.ForeignKey(User, verbose_name='Modérateur', related_name='+')
    # TODO: définir ceci en fonction de la date du starting_message
    start_date = models.DateTimeField(verbose_name='Date de démarrage', blank=True, null=True,
                                        db_index=True)
    # TODO: définir ceci en fonction de la date du ending_message
    end_date = models.DateTimeField(verbose_name='Date de fin', blank=True, null=True)
    start_message = models.ForeignKey(Message, verbose_name='Message d\'annonce',
                                         related_name='+', blank=True, null=True)
    end_message = models.ForeignKey(Message, verbose_name='Message de cloture',
                                       related_name='+', blank=True, null=True)

    class Meta:
        abstract = True
        ordering = ['date_started']

    def start(self):
        assert self.start_date is None
        self.start_date = datetime.now()
        self.clean()
        self.save()

    def stop(self):
        assert self.end_date is None
        self.end_date = datetime.now()
        self.clean()
        self.save()

class Season(DatestampedWithMessagesAndAuthor):
    number = models.SmallIntegerField(verbose_name='Numéro')
    title = models.CharField(verbose_name='Titre', max_length=80)
    slug = models.SlugField(max_length=90)
    description = models.TextField(verbose_name='Description', help_text='Description de la saison')

    class Meta:
        verbose_name = 'Saison'

class Turn(DatestampedWithMessagesAndAuthor):
    number = models.SmallIntegerField(verbose_name='Numéro', blank=True, null=True)
    season = models.ForeignKey('Season', verbose_name='Saison', blank=True, null=True)
    # Todo: check unicity of (Season, Number)
    # Todo: Prevent a turn to be started if another one is started
    # Todo: Ensure turn numbers are right

    class Meta:
        verbose_name = 'Manche'

    def __str__(self):
        if not self.number:
            return 'Manche détachée'
        else:
            return 'Manche %s de la saison %s' % (self.number, self.season.number)

    def attach(self, season):
        """Attach a turn from a season."""
        self.season = season
        self.save()

    def detach(self, season):
        """Detach a turn from a season. Runs clean(), which should delete start and end dates."""
        # TODO Check that there are no attached answers
        self.season = None
        self.clean()
        self.save()

    def clean(self):
        """If there is no season, start_date and end_date should be unset."""
        if self.season is None:
            self.start_date = None
            self.end_date = None

class Question(models.Model):
    author = models.ForeignKey(User, related_name='+', verbose_name='Author', blank=True)
    turn = models.ForeignKey(Turn, verbose_name='Manche', blank=True, null=True)
    text = models.CharField(verbose_name='Texte', max_length=80, blank=True)
    # Todo: prevent questions to be changed when they are attached to a started session

    @property
    def season(self):
        return self.turn.season if self.turn else None

    class Meta:
        verbose_name = 'Question'

class Subscription(models.Model):
    """
    Pseudo OneToOne through model between Season and User.
    This class is used to send appropriate notifications to the users.
    """
    season = models.ForeignKey(Season)
    user = models.ForeignKey(User, related_name='+')

    class Meta:
        verbose_name = 'Inscription'

