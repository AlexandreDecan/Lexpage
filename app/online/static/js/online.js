var online_ping_url;

function online_init_ping(ping_url, online_timeout){
    // online_timeout is in minutes
    // We take the timeout minus 5 seconds
    var online_delay = 60000 * online_timeout - 5000;
    online_ping_url = ping_url;
    setInterval(online_ping, online_delay);
}

function online_ping() {
    $.get(online_ping_url);
}
