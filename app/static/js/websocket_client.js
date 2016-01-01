// Taken from django-websocket-redis/ws4redis/static/js/ws4redis.js
// License: MIT
function WebsocketClient(options, $) {
    'use strict';
    var opts, ws, deferred, timer, attempts = 1;
    var heartbeat_interval = null, missed_heartbeats = 0;

    if (this === undefined)
        return new WebsocketClient(options, $);
    if (options.uri === undefined)
        throw new Error('No Websocket URI in options');
    if ($ === undefined)
        $ = jQuery;
    opts = $.extend({ heartbeat_msg: null }, options);
    connect(opts.uri);

    function connect(uri) {
        console.log('connecting to '+uri)
        try {
            deferred = $.Deferred();
            ws = new WebSocket(uri);
            ws.onopen = on_open;
            ws.onmessage = on_message;
            ws.onerror = on_error;
            ws.onclose = on_close;
            timer = null;
        } catch (err) {
            deferred.reject(new Error(err));
        }
    }

    function send_heartbeat() {
        try {
            missed_heartbeats++;
            if (missed_heartbeats > 3) {
                on_missed_heartbeat();
                throw new Error("Too many missed heartbeats.");
            }
            console.log('sending heartbeat')
            ws.send(opts.heartbeat_msg);
        } catch(e) {
            clearInterval(heartbeat_interval);
            heartbeat_interval = null;
            console.warn("Closing connection. Reason: " + e.message);
            ws.close();
        }
    }

    function on_heartbeat() {
        if (typeof opts.on_heartbeat === 'function') {
            opts.on_heartbeat();
        }
    }

    function on_missed_heartbeat() {
        if (typeof opts.on_missed_heartbeat === 'function') {
            opts.on_missed_heartbeat();
        }
    }

    function on_open() {
        console.log('connected')
        if (typeof opts.on_open === 'function') {
            opts.on_open();
        }
        // new connection, reset attemps counter
        deferred.resolve();
        if (opts.heartbeat_msg && heartbeat_interval === null) {
            missed_heartbeats = 0;
            heartbeat_interval = setInterval(send_heartbeat, 5000);
        }
    }

    this.reconnect = function() {
        attempts = 1;
        if (timer) {
            clearInterval(timer);
        }
        try {
            ws.close();
        } catch(e) {
            console.log('could not close ws:' + e.message);
        }
        connect(ws.url+'&r');
    }

    function on_close(evt) {
        console.log('connection closed')
        if (typeof opts.on_close === 'function') {
            opts.on_close(evt.data);
        }
        if (!timer) {
            // try to reconnect
            var interval = generateInteval(attempts);
            timer = setTimeout(function() {
                attempts++;
                connect(ws.url);
            }, interval);
        }
    }

    function on_error(evt) {
        console.error("Websocket connection is broken!");
        deferred.reject(new Error(evt));
        if (typeof opts.on_error === 'function') {
            opts.on_error(evt.data);
        }
    }

    function on_message(evt) {
        if (opts.heartbeat_msg && evt.data === opts.heartbeat_msg) {
            // reset the counter for missed heartbeats
            missed_heartbeats = 0;
            on_heartbeat();
        } else if (typeof opts.receive_message === 'function') {
            return opts.receive_message(evt.data);
        }
    }

    // this code is borrowed from http://blog.johnryding.com/post/78544969349/
    //
    // Generate an interval that is randomly between 0 and 2^k - 1, where k is
    // the number of connection attmpts, with a maximum interval of 30 seconds,
    // so it starts at 0 - 1 seconds and maxes out at 0 - 30 seconds
    function generateInteval (k) {
        var maxInterval = (Math.pow(2, k) - 1) * 1000;

        // If the generated interval is more than 30 seconds, truncate it down to 30 seconds.
        if (maxInterval > 30*1000) {
            maxInterval = 30*1000;
        }

        // generate the interval to a random number between 0 and the maxInterval determined from above
        return Math.random() * maxInterval;
    }

    this.send_message = function(message) {
        ws.send(message);
    };
}
