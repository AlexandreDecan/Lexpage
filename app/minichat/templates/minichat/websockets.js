jQuery(document).ready(function($) {
    websocket_minichat = WS4RedisImproved({
        uri: '{{ WEBSOCKET_URI }}minichat?subscribe-broadcast&echo{% if debug %}&ts={% now "U" %}{% endif %}',
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
        // timeout to prevent this to be shown on page refresh
        setTimeout(function(){
            if (minichat_timer_enabled) {
                minichat_toggle_notification(false);
            }
        }, 1000);
    }
    function receiveMessage(msg) {
        minichat_refresh();
    }
});
