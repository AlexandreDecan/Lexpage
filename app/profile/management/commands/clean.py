from django.core.management.base import NoArgsCommand

from registration.models import ActivationKey


class Command(NoArgsCommand):
    help = "Delete expired user registrations from the database"

    def handle_noargs(self, **options):
        ActivationKey.objects.delete_expired()
