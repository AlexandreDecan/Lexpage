from django import template
from ..models import Notification

register = template.Library()

@register.assignment_tag(takes_context=True)
def notifications(context):
    if 'user' in context: 
        return Notification.objects.filter(recipient=context['user'])
