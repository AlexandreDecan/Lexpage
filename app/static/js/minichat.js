var minichat_timer_delay = 30000;
var minichat_content;
var minichat_content_url;
var minichat_post_url;

var minichat_form = "#minichat_form";
var minichat_button = "#minichat_form button[type='submit']";
var minichat_input_text = "#minichat_form input[type='text']";
var minichat_chars_output = "#minichat_form .minichat-remainingChars";


function minichat_init_display(content, get_url) {
    minichat_content = content
    minichat_content_url = get_url;
    
    if (minichat_content) {
        setInterval(minichat_refresh, minichat_timer_delay);
        minichat_refresh();
    }
}

function minichat_refresh() {
    $.get(minichat_content_url, function(data) {
        $(minichat_content).html(data);
        replace_invalid_avatar($(minichat_content));
        activate_tooltips($(minichat_content));
    });
}

function minichat_init_post() {
    minichat_post_url = $(minichat_form).attr("action");

    $(minichat_button).click(
        function(e) {
            e.preventDefault();
            $(minichat_button).find('span').addClass('fa-spinner fa-spin');
            minichat_post_message();
        }
    );
}

function minichat_post_message() {
    $.post(minichat_post_url, $(minichat_form).serialize())
        .done(function(data) {
            $(minichat_button).find('span').removeClass('fa-spinner fa-spin fa-warning btn-warning');
            $(minichat_input_text).val("");
            minichat_update_chars_count();
            minichat_refresh();
        })
        .fail(function(data) {
            $(minichat_button).find('span').removeClass('fa-spinner fa-spin').addClass('fa-warning');
            minichat_refresh();
        });
}

function minichat_update_chars_count() {
    var remaining = $(minichat_input_text).attr("maxlength") - $(minichat_input_text).val().length;
    var plural = "";
    if (remaining > 1) plural = "s";
    $(minichat_input_text).parent().toggleClass("has-warning", remaining == 0);
    $(minichat_chars_output).text(remaining + "  caractère"+plural+" restant"+plural);
}

function minichat_init_remaining_chars() {
    minichat_update_chars_count();
    $(minichat_input_text).change(minichat_update_chars_count);
    $(minichat_input_text).keyup(minichat_update_chars_count);
}
