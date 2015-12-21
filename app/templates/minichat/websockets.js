var transport = WebSocket;
var endpoint = '{{ OMNIBUS_ENDPOINT }}';
var options = {
    authToken: '{{ OMNIBUS_AUTH_TOKEN }}'
};

var connection = new Omnibus(transport, endpoint, options);
var channel = connection.openChannel('minichat');

connection.on(Omnibus.events.CONNECTION_AUTHENTICATED, function(event) {
    minichat_refresh();
    input = document.querySelector('#minichat_form input.form-control');
    if (input) { input.disabled = false; }
});

connection.on(Omnibus.events.CONNECTION_DISCONNECTED, function(event) {
    input = document.querySelector('#minichat_form input.form-control');
    if (input) { input.disabled = true; }
});

channel.on('new-message', function(event){
    minichat_refresh();
});
