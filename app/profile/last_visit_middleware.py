from datetime import datetime
from .models import Profile


class SetLastVisitMiddleware():
    def process_response(self, request, response):
        if hasattr(request, 'user'):
            if request.user.is_authenticated():
                Profile.objects.filter(user=request.user).update(last_visit=datetime.now())
        return response
