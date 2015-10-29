from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class MarkupPreviewView(TemplateView):
    template_name = 'commons/markup_preview.html'

    dispatch = method_decorator(login_required)(TemplateView.dispatch)

    def get_context_data(self, **kwargs):
        context = super(MarkupPreviewView, self).get_context_data(**kwargs)

        context['markup'] = kwargs['markup']
        try:
            context['content'] = self.request.GET['content']
        except KeyError:
            pass
        return context
