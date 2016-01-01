var websocket_status = false;
jQuery(document).ready(function($) {
    lexpage_websocket = WebsocketClient({
        uri: '{{ WEBSOCKET_URI }}lexpage?subscribe-user&subscribe-broadcast&echo{% if debug %}&ts={% now "U" %}{% endif %}',
        receive_message: receiveMessage,
        on_heartbeat: onOpen,
        on_missed_heartbeat: onClose,
        on_close: onClose,
        heartbeat_msg: {{ WS4REDIS_HEARTBEAT }}
    });

    function onOpen() {
        if(!websocket_status) {
            websocket_status = true;
            minichat_websocket_onOpen();
        }
    }

    function onClose() {
        if(websocket_status) {
            websocket_status = false;
            minichat_websocket_onClose();
        }
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
