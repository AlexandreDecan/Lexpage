var notifications_content_url;
var notifications_content;
var notifications_button_content_url;
var notifications_button_content;
var notifications_dropdown;
var notifications_counter;

function notifications_init_display(content, counter, dropdown, get_url) {
    notifications_content_url = get_url;
    notifications_content = content;
    notifications_dropdown = dropdown;
    notifications_counter = counter;
}

function notifications_button_init_display(content, get_url) {
    notifications_button_content_url = get_url;
    notifications_button_content = content;
}

function notifications_refresh(count) {
    notifications = parseInt(count);
    if (notifications == 0){
        $(notifications_content).hide();
    } else {
        $(notifications_content).show();
        $(notifications_counter).html("<span class=\"fa fa-bell\"> "+count);
    }
    $.get(notifications_content_url, function(data) {
        $(notifications_dropdown).html(data);
        notification_initialize();
    });
    $.get(notifications_button_content_url, function(data) {
        $(notifications_button_content).html(data);
    });
}
