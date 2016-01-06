from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class MarkupPreviewView(TemplateView):
    template_name = 'commons/markup_preview.html'

    @method_decorator(login_required)
    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        context = super(MarkupPreviewView, self).get_context_data(**kwargs)

        context['markup'] = kwargs['markup']
        try:
            context['content'] = self.request.POST['content']
        except KeyError:
            pass
        return super().render_to_response(context)
