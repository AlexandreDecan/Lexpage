jQuery(document).ready(function($) {
    websocket_minichat = WS4RedisImproved({
        uri: '{{ WEBSOCKET_URI }}minichat?subscribe-broadcast&echo',
        receive_message: receiveMessage,
        on_open: onOpen,
        on_close: onClose,
        heartbeat_msg: {{ WS4REDIS_HEARTBEAT }}
    });

    function onOpen() {
        minichat_refresh();
        minichat_toggle_notification(true);
    }
    function onClose() {
        minichat_refresh();
        minichat_toggle_notification(false);
    }
    function receiveMessage(msg) {
        minichat_refresh();
    }
});
