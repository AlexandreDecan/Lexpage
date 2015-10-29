from django.core.management.base import NoArgsCommand

from blog.models import BlogPost

import datetime

"""
class Command(NoArgsCommand):
    help = "Publish the first available blog entry. "

    def handle_noargs(self, **options):
        try:
            post = BlogPost.approved.all()[0]
            post.change_status(None, BlogPost.STATUS_PUBLISHED)
            return 'publish: %s' % post.title
        except IndexError:
            return 'No blog entry available!?'
"""


class Command(NoArgsCommand):
    help = "Publish the first available blog entry. "

    # (min available, nb per day)
    number_per_day = [(8, 2), (1, 1)]
    # number_per_day = [(1, 2), ]

    def handle_noargs(self, **options):
        try:
            # If it's sunday, dismiss
            if datetime.datetime.now().weekday() == 6:
                return None

            # Dismiss in case of public holiday
            day, month = (datetime.date.today().day, datetime.date.today().month)
            if (day, month) in [(1, 1), (1, 5), (14, 7), (21, 7), (15, 8), (1, 11), (11, 11), (25, 12)]:
                return 'Public holiday'

            # Get number of available posts
            posts = BlogPost.approved.all()
            nb_posts = len(posts)
            if nb_posts == 0:
                # No post? no post!
                return 'No available post'

            # nb_per_day contains the number of posts per day wrt the stock
            nb_per_day = 0
            for min_post, nb_post in Command.number_per_day:
                if nb_posts >= min_post:
                    nb_per_day = nb_post
                    break

            # Time since last published post, in hours
            delta = (datetime.datetime.now() - BlogPost.published.latest().date_published)
            delta = (delta.seconds + delta.days * 24 * 3600) // 3600.0
            delta += 0.5  # Dismiss OVH delay

            # If delta (in hour) > time_frame, publish!
            if delta >= (24 / nb_per_day):
                posts[0].change_status(None, BlogPost.STATUS_PUBLISHED)
                return 'Task: publish "%s"' % str(posts[0].title)
            else:
                return None
        except Exception as e: 
            return str(e)
