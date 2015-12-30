jQuery(document).ready(function($) {
    lexpage_websocket = WS4RedisImproved({
        uri: '{{ WEBSOCKET_URI }}lexpage?subscribe-user&subscribe-broadcast&echo{% if debug %}&ts={% now "U" %}{% endif %}',
        receive_message: receiveMessage,
        on_open: onOpen,
        on_close: onClose,
        heartbeat_msg: {{ WS4REDIS_HEARTBEAT }}
    });

    function onOpen() {
        minichat_websocket_onOpen();
    }

    function onClose() {
        minichat_websocket_onClose();
    }

    function receiveMessage(raw_msg) {
        msg = JSON.parse(raw_msg);
        if ('app' in msg) {
            if (msg['app'] == 'minichat'){
                minichat_websocket_receiveMessage(msg);
            }
            else if (msg['app'] == 'notifications'){
                notifications_websocket_receiveMessage(msg);
            }
        }
    }
});
