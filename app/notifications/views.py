from django.views.generic import View, RedirectView
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from .models import Notification

class ShowView(RedirectView):
    permanent = False

    dispatch = method_decorator(login_required)(View.dispatch)

    def get_redirect_url(self, **kwargs):
        notification = get_object_or_404(Notification.objects, pk=kwargs['pk'], recipient=self.request.user.pk)
        notification.dismiss()
        return notification.action
