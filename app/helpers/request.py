def is_incognito(request):
    """Returns True if the current session is an incognito session"""
    if not hasattr(request, 'user') or not request.user.is_authenticated():
        return True
    if hasattr(request, 'session') and 'incognito' in request.session:
        incognito = request.session['incognito']
    else:
        incognito = True
    return incognito
