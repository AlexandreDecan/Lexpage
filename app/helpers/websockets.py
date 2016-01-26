def get_allowed_channels(request, channels):
    """ Returns the allowed channels. We only allow subscribe channels and for
    authenticated users only."""
    allowed_channels = []
    if request.user and request.user.is_authenticated():
        allowed_channels.append('subscribe-broadcast')
        allowed_channels.append('subscribe-user')
    allowed_channels = set(channels).intersection(allowed_channels)
    return allowed_channels
