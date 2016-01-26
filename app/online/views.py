from django.http import HttpResponse

def online_ping(request):
    """A view used to keep the user alive in the connected users list"""
    return HttpResponse('pong')
