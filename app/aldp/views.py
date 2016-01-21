from django.views.generic.edit import FormView
from django.contrib.auth.decorators import permission_required
from django.utils.decorators import method_decorator

from .forms import SeasonForm

# Create your views here.
class SeasonCreateView(FormView):
    """
    Create a new thread and display its content on form submission.
    """

    template_name = 'aldp/season_create.html'
    form_class = SeasonForm
    success_url = '/'

    dispatch = method_decorator(permission_required('aldp.create_season'))(FormView.dispatch)
