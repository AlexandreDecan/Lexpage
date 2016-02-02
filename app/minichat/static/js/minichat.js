"use strict";

var app_minichat = {
    timer_delay: 10,  // Incremented if not loggued
    split_delay: 5 * 60,

    content_url: null,
    template_url: "minichat/latests.html",

    username: null,
    read_date: null,

    container_selector: null,
    form_selector: null,

    _form_selector: null,
    _button_selector: null,
    _input_text_selector: null,
    _remaining_chars_selector: null,

    init: function (username, last_visit, container_selector, form_selector, content_url) {
        if (!username || username == "")
            app_minichat.timer_delay = 30;

        app_minichat.username = username;
        app_minichat.read_date = last_visit;
        app_minichat.container_selector = container_selector;
        app_minichat.form_selector = form_selector;
        app_minichat.content_url = content_url;

        app_minichat._form_selector = form_selector;
        app_minichat._button_selector = form_selector + " button[type='submit']";
        app_minichat._input_text_selector = form_selector + " input[type='text']";
        app_minichat._remaining_chars_selector = form_selector + " .minichat-remainingChars";

        $(app_minichat._button_selector).click(function(e) {
            e.preventDefault();
            $(app_minichat._button_selector).find('span').addClass('fa-spinner fa-spin');
            app_minichat.post_message();
        });

        app_minichat.update_chars_count();
        $(app_minichat._input_text_selector).change(app_minichat.update_chars_count);
        $(app_minichat._input_text_selector).keyup(app_minichat.update_chars_count);

        app_minichat.refresh();
        setInterval(app_minichat.refresh, app_minichat.timer_delay * 1000);
    },

    group_messages: function(messages) {
        // Group by date
        var date_groups = _.groupBy(messages, function (e) {
            return moment(e.date).format("YYYY-MM-DD");
        });

        // Group by author inside each groups
        return _.map(date_groups, function (messages, date) {
            var last_message = null;
            var groups = [];
            var group;
            for (var i = 0; i < messages.length; i++) {
                var message = messages[i];

                if (!last_message || (last_message.user.username != message.user.username) ||
                    (moment(last_message.date).diff(moment(message.date), 'seconds') >= app_minichat.split_delay)) {
                    if (group)
                        groups.push(group);
                    group = {'user': message.user, 'messages': []};
                }

                last_message = message;
                group.messages.push(message);
            }
            groups.push(group);
            return {'date': date, 'groups': groups};
        });
    },

    reset: function() {
        app_minichat.refresh_content_with([]);
    },

    refresh_content_with: function(data) {
        var messages = app_minichat.group_messages(data);

            var context = {dates: messages, 'current_username': app_minichat.username, 'read_date': app_minichat.read_date};
            $(app_minichat.container_selector).html(nunjucks.render(app_minichat.template_url, context));
            replace_invalid_avatar($(app_minichat.container_selector));
            activate_tooltips($(app_minichat.container_selector));
    },

    refresh: function () {
        $.get(app_minichat.content_url, function (data) {
            app_minichat.refresh_content_with(data.results)
        });
    },

    post_message: function () {
        $.post($(app_minichat.form_selector).attr("action"), $(app_minichat.form_selector).serialize())
            .done(function(data) {
                if (data.substituted) {
                    contrib_message("info", "Votre dernier message est devenu \"<em>"+ data.substituted.text +"</em>\".");
                } else if (data.anchors.length > 0) {
                    var beautified_users;
                    if (data.anchors.length > 1) {
                        var users = data.anchors.join(', à ');
                        var comma = users.lastIndexOf(', à ');
                        beautified_users = users.substr(0, comma) + ' et' + users.substr(comma+1)
                    } else {
                        beautified_users = data.anchors[0];
                    }
                    contrib_message("info", "Une notification a été envoyée à " + beautified_users + ".")
                }
                $(app_minichat._button_selector).find('span').removeClass('fa-spinner fa-spin fa-warning btn-warning');
                $(app_minichat._input_text_selector).val("");
                app_minichat.update_chars_count();
                app_minichat.refresh();
            })
            .fail(function() {
                    $(app_minichat._button_selector).find('span').removeClass('fa-spinner fa-spin').addClass('fa-warning');
                    app_minichat.refresh();
                }
            );
    },

    update_chars_count: function () {
        var remaining = $(app_minichat._input_text_selector).attr("maxlength") - $(app_minichat._input_text_selector).val().length;
        var plural;
        if (remaining > 1) plural = "s"; else plural = "";

        $(app_minichat._input_text_selector).parent().toggleClass("has-warning", remaining == 0);
        $(app_minichat._remaining_chars_selector).text(remaining + "  caractère"+plural+" restant"+plural);
    }
};

