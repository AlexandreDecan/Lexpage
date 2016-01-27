from datetime import datetime

from helpers.request import is_incognito
from profile.models import Profile


class SetLastVisitMiddleware():
    def process_response(self, request, response):
        if not is_incognito(request):
            Profile.objects.filter(user=request.user).update(last_visit=datetime.now())
        return response
