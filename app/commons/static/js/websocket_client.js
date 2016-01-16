// Derived from django-websocket-redis/ws4redis/static/js/ws4redis.js
// License: MIT


function WebsocketClient(options, $) {
    'use strict';
    var opts, ws, deferred, timer, attempts = 1;
    var callbacks = {'on_message':{}, 'on_connect':{}, 'on_disconnect':{}};
    var heartbeat_interval = null, missed_heartbeats = 0;
    var websocket_status = false;

    if (this === undefined)
        return new WebsocketClient(options, $);
    if ($ === undefined)
        $ = jQuery;
    opts = $.extend({ heartbeat_msg: null }, options);

    this.register = function(application, method, callback) {
        callbacks[method][application] = callback;
    };

    this.isConnected = function(){
        return websocket_status;
    }

    this.connect = function(uri) {
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
                connection_dead();
                throw new Error("Too many missed heartbeats.");
            }
            ws.send(opts.heartbeat_msg);
        } catch(e) {
            clearInterval(heartbeat_interval);
            heartbeat_interval = null;
            console.warn("Closing connection. Reason: " + e.message);
            ws.close();
        }
    }

    function call_all_callbacks(method) {
        for (var application in callbacks[method]) {
            var cb = callbacks[method][application];
            cb();
        }
    }

    function connection_alive() {
        if(!websocket_status) {
            websocket_status = true;
            call_all_callbacks('on_connect');
        }
    }

    function connection_dead() {
        if(websocket_status) {
            websocket_status = false;
            call_all_callbacks('on_disconnect');
        }
    }

    function on_missed_heartbeat() {
        connection_dead();
    }

    function on_open() {
        deferred.resolve();
        if (opts.heartbeat_msg && heartbeat_interval === null) {
            missed_heartbeats = 0;
            heartbeat_interval = setInterval(send_heartbeat, 5000);
        }
    }

    function on_close(evt) {
        if (!timer) {
            connection_dead();
            // try to reconnect
            var interval = generateInteval(attempts);
            timer = setTimeout(function() {
                attempts++;
                this.connect(ws.url);
            }, interval);
        }
    }

    function on_error(evt) {
        connection_dead();
        console.error("Websocket connection is broken!");
        deferred.reject(new Error(evt));
    }

    function on_message(evt) {
        if (opts.heartbeat_msg && evt.data === opts.heartbeat_msg) {
            // reset the counter for missed heartbeats
            missed_heartbeats = 0;
            connection_alive();
        } else {
            var data = JSON.parse(evt.data);
            var application = data['app'];
            if (application in callbacks['on_message']) {
                var cb = callbacks['on_message'][application];
                cb(data);
            }
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

