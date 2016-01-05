Websockets Support
==================

The library used to handle websockets is
[django-websocket-redis][ws4redis].

It has been chosen for the following reasons:
- It's a popular, maintained library
- Uses redis as a backend. Redis is very popular, so we should not have
  too much troubles with it.

We use the library on the server side and the client side.

It means that if you want a full instance of Lexpage running with all
the features, you will need a redis server running. If you don't, you
will not be able to have the refresh of the minichat and the
notifications.

[ws4redis]:http://django-websocket-redis.readthedocs.org/en/latest/usage.html

How we implemented websockets
=============================

On the client side, we use an improved javascript library that
originally came from the django-websocket-redis. The modifications done
are for adding extra callback functions.

On the server side, we use the Django Signals mechanism to send the
messages. It means that it does not matter the place in the code where
we actually change a model, each change will create a websocket event.

We currently use one websocket for 2 purposes:

Minichat
--------

As the minichat already implemented some kind of refresh, we decided to
simply reuse that code but trigger it with the websocket, removing the
need to refresh on a regular basis.

When you post a message, the minichat will only be notified by the
websocket. Before, it was refreshed by the chat form itself.

The content of the websocket message does not contain anything useful,
as it is just a trigger for a full reload of the minichat `<div>`.

That websocket uses the 'broadcast' events, so the events are sent to
anyone.

From the user point of view, when the connection to the websocket is
not active, the textinput for the minichat is disabled. This will help
user to see if the chat is live or not, and hopefully help them to see
when there are troubles with websockets.

Notifications
-------------

The notifications websocket works as the minichat one, with the
difference that two places are updated: one for the desktop view and one
for the mobile view.

That websocket uses the 'subscribe-user' events, so you only get the
notifications for the current user (and you are not informed when other
users' notifications change).

The content of the messages contains the number of notifications for the user.

