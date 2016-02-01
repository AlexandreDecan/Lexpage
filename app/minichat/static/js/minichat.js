app_minichat = function (username, last_visit, ws_client) {
    var _timer_delay = 30;
    var _split_delay = 5 * 60;

    var _content_url;
    var _template_url = "minichat/latests.html";

    var _ws_client = ws_client;
    var _username = username;
    var _read_date = last_visit;

    var _replace_invalid_avatar = replace_invalid_avatar; // Need to be set outside!
    var _activate_tooltips = activate_tooltips; // Need to be set outside!
    var _contrib_message = contrib_message; // Need to be set outside!

    var _container_selector;
    var _form_selector;
    var _button_selector;
    var _input_text_selector;
    var _remaining_chars_selector;

    var app = this;


    this.init_display = function(container_selector, form_selector, content_url) {
        _container_selector = container_selector;
        _content_url = content_url;

        _form_selector = form_selector;
        _button_selector = _form_selector + " button[type='submit']";
        _input_text_selector = _form_selector + " input[type='text']";
        _remaining_chars_selector = _form_selector + " .minichat-remainingChars";

        // Register if available
        if (_ws_client){
            ws_client.register('minichat', 'on_message', function(data) {
                if (data.action == "reload_minichat") {
                    app.refresh_content();
                }
            });
        }

        setInterval(function () {
            // If not connected, use fallback
            if (!_ws_client || !_ws_client.isConnected()) {
                app.refresh_content();
            }
        });

        $(_button_selector).click(function(e) {
                e.preventDefault();
                $(_button_selector).find('span').addClass('fa-spinner fa-spin');
                app.post_message();
        });
        this.update_chars_count();
        $(_input_text_selector).change(this.update_chars_count);
        $(_input_text_selector).keyup(this.update_chars_count);

        this.refresh_content();
    };

    this.group_messages = function(messages) {
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
                    (moment(last_message.date).diff(moment(message.date), 'seconds') >= _split_delay)) {
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
    };

    this.refresh_content = function () {
        $.get(_content_url, function (data) {
            var messages = app.group_messages(data.results);

            var context = {dates: messages, 'current_username': _username, 'read_date': _read_date};
            $(_container_selector).html(nunjucks.render(_template_url, context));
            _replace_invalid_avatar($(_container_selector));
            _activate_tooltips($(_container_selector));
        });
    };

    this.post_message = function () {
        $.post($(_form_selector).attr("action"), $(_form_selector).serialize())
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
                    _contrib_message("info", "Une notification a été envoyée à " + beautified_users + ".")
                }
                $(_button_selector).find('span').removeClass('fa-spinner fa-spin fa-warning btn-warning');
                $(_input_text_selector).val("");
                app.update_chars_count();
                app.refresh_content();
            })
            .fail(function() {
                $(_button_selector).find('span').removeClass('fa-spinner fa-spin').addClass('fa-warning');
                app.refresh_content();
            }
        );
    };

    this.update_chars_count = function () {
        var remaining = $(_input_text_selector).attr("maxlength") - $(_input_text_selector).val().length;
        var plural;
        if (remaining > 1) plural = "s"; else plural = "";

        $(_input_text_selector).parent().toggleClass("has-warning", remaining == 0);
        $(_remaining_chars_selector).text(remaining + "  caractère"+plural+" restant"+plural);
    };

    return this;
};
