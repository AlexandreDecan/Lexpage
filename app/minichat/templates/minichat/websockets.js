jQuery(document).ready(function($) {
    var ws4redis = WS4RedisImproved({
        uri: '{{ WEBSOCKET_URI }}minichat?subscribe-broadcast&echo',
        receive_message: receiveMessage,
        on_open: onOpen,
        on_close: onClose,
        heartbeat_msg: {{ WS4REDIS_HEARTBEAT }}
    });

    function onOpen() {
        console.log('foo');
        minichat_refresh();
        input = document.querySelector('#minichat_form input.form-control');
        if (input) { input.disabled = false; }
    }
    function onClose() {
        input = document.querySelector('#minichat_form input.form-control');
        if (input) { input.disabled = true; }
    }
    function receiveMessage(msg) {
        minichat_refresh();
    }
});
