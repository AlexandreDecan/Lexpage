jQuery(document).ready(function($) {
    WS4RedisImproved({
        uri: '{{ WEBSOCKET_URI }}notifications?subscribe-user&echo',
        receive_message: receiveNotification,
        heartbeat_msg: {{ WS4REDIS_HEARTBEAT }}
    });

    function receiveNotification(count) {
        notifications_refresh(count);
    }
});
