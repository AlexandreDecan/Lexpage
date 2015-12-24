def get_allowed_channels(request, channels):
    """ Returns the allowed channels. We allow subscribe-broadcast to anyone,
    and subscribe-user for authenticated users. This is used for the client
    side only."""
    allowed_channels = ['subscribe-broadcast']
    if request.user and request.user.is_authenticated():
        allowed_channels.append('subscribe-user')
    allowed_channels = set(channels).intersection(allowed_channels)
    return allowed_channels

