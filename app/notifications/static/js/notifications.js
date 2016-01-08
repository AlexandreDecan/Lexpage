var notifications_menu_button;
var notifications_dropdown_button;
var notifications_content_list;
var notifications_content_url;

var notifications_button_template = "/notifications/button.html";
var notifications_list_template = "/notifications/list.html";

nunjucks.configure({ autoescape: false });

function notifications_init_display(menu_button, dropdown_button, content_list, get_url) {
    notifications_menu_button = menu_button;
    notifications_dropdown_button = dropdown_button;
    notifications_content_list = content_list;
    notifications_content_url = get_url;

    notifications_refresh();
}

function notifications_refresh() {
    $.get(notifications_content_url, function(data) {
        data_embedded = { 'notifications_list': data };
        if (data.length == 0) { $(notifications_dropdown_button).hide(); } else {$(notifications_dropdown_button).show();}
        $(notifications_dropdown_button).html(nunjucks.render(notifications_button_template, data_embedded));
        $(notifications_content_list).html(nunjucks.render(notifications_list_template, data_embedded));
        $(notifications_menu_button).html(nunjucks.render(notifications_button_template, data_embedded));
        notification_initialize();
    });
}

function notification_initialize() {
    $(".notification_list .notification_dismiss a.close").click(function (e) {
        e.stopPropagation(); // Prevent dropdown to close
    });
}

function notification_dismiss(url, target) {
    // Disable click propagation (to keep dropdown opened)
    function done(data) {
        // Dismiss target
        notifications_refresh();
    }
    $("#"+target+" a.close").addClass("fa-spinner fa-spin");
    $.ajax({url: url, type: 'DELETE'}).done(done);
}
