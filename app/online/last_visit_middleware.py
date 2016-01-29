from datetime import datetime

from helpers.request import is_incognito
from profile.models import Profile


class SetLastVisitMiddleware():
    def process_response(self, request, response):
        if not is_incognito(request) and response.status_code != 302:
            # We ignore status code 302 so the last_visit is not updated at the login page redirect
            # Without this, when a user would log in, the last_visit datetime would be the login
            # time and not the time we reach the home page.
            Profile.objects.filter(user=request.user).update(last_visit=datetime.now())
        return response
