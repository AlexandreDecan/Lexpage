from django import template
from ..models import Slogan

register = template.Library()


def random_slogan():
    slogan = Slogan.visible.get_random()
    return slogan

register.simple_tag(random_slogan)
