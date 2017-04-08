from django import template
from profile.models import ActiveUser

from django.db.models import Q

import datetime


register = template.Library()


def birthday():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(1)
    tomorrow = today + datetime.timedelta(1)

    q_yesterday = Q(profile__birthdate__day=yesterday.day, profile__birthdate__month=yesterday.month)
    q_today = Q(profile__birthdate__day=today.day, profile__birthdate__month=today.month)
    q_tomorrow = Q(profile__birthdate__day=tomorrow.day, profile__birthdate__month=tomorrow.month)
    
    u_yesterday = ActiveUser.objects.filter(q_yesterday)
    u_today = ActiveUser.objects.filter(q_today)
    u_tomorrow = ActiveUser.objects.filter(q_tomorrow)
    
    return list(u_yesterday) + list(u_today) + list(u_tomorrow)

register.simple_tag(birthday)
