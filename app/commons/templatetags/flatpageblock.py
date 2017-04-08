from django import template
from django.contrib.flatpages.models import FlatPage
from django.utils.safestring import mark_safe

register = template.Library()


def flatpageblock(flatpage):
    """
    Provide the title, the url and the content of the flatpage whose 
    url is given by 'flatpage'. 
    """
    try:
        flatpage_ = FlatPage.objects.get(url=flatpage)
        return {'title': mark_safe(flatpage_.title), 
                'url': flatpage_.url,
                'content': mark_safe(flatpage_.content)}
    except FlatPage.DoesNotExist:
        return None

register.simple_tag(flatpageblock)
