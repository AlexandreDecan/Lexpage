from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Turn

@receiver(post_save, sender=Turn)
def update_season_start_date(sender, **kwargs):
    """ After Saving a turn, update the season start_date if needed."""
    if not kwargs.get('raw', False): # check that this is not a fixture
        turn = kwargs['instance']
        if turn.season and turn.season.start_date is None:
            turn.season.start_date = turn.start_date
            turn.season.save()

