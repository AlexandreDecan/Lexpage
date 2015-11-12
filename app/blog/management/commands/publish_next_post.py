from django.core.management.base import NoArgsCommand
from blog.models import BlogPost
import datetime


class Command(NoArgsCommand):
    help = "Publish the first available blog entry. "

    # (min available, nb per day)
    number_per_day = [(8, 2), (1, 1), (0, 0)]
    # number_per_day = [(1, 2), ]

    def handle_noargs(self, **options):
        today = datetime.date.today()

        # Do not publish on sunday and in public holiday
        if today.weekday() == 6:
            return 'No post on sunday'
        if (today.day, today.month) in [(1, 1), (1, 5), (14, 7), (21, 7), (15, 8), (1, 11), (11, 11), (25, 12)]:
            return 'No post on public holiday'

        # Number of already published posts for today
        published = len(BlogPost.published.filter(date_published__gte=today))

        # Number of available posts for today
        available = len(BlogPost.approved.all())
        if available == 0:
            return 'No available post'

        # Expected number of posts for today
        expected = list(filter(lambda x: (published + available) >= x[0], Command.number_per_day))[0][1]
        if published == expected:
            return None

        # Time between each post for today
        delay = (24 * 3600) / expected

        # Time of latest published post today
        try:
            latest_post = BlogPost.published.filter(date_published__gte=today).order_by('date_published').last()
            latest_delay = (datetime.datetime.now() - latest_post.date_published).total_seconds()
        except Exception:
            latest_delay = 10 * delay  # Ensure a new publication

        # Do we publish?
        if latest_delay + 600 >= delay:  # Add 10 minutes to latest_delay as cron job are not very accurate
            post = BlogPost.approved.first()
            post.change_status(None, BlogPost.STATUS_PUBLISHED)
            return 'Publish %s' % post.title
