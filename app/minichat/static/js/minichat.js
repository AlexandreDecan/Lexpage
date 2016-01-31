function create_minichat(username, last_visit, ws_client) {
    var _timer_delay = 30;
    var _split_delay = 5 * 60;

    var _content_url;
    var _post_url;
    var _template_url = "minichat/latests.html";

    var _ws_client = ws_client;
    var _username = username;
    var _read_date = last_visit;

    var _replace_invalid_avatar = replace_invalid_avatar; // Need to be set outside!
    var _activate_tooltips = activate_tooltips; // Need to be set outside!
    var _contrib_message = contrib_message; // Need to be set outside!

    var _content_selector;
    var _form_selector = "#minichat_form";
    var _button_selector = "#minichat_form button[type='submit']";
    var _input_text_selector = "#minichat_form input[type='text']";
    var _remaining_chars_selector = "#minichat_form .minichat-remainingChars";

    var minichat = this;


    this.init_display = function(content_selector, content_url) {
        _content_selector = content_selector;
        _content_url = content_url;

        if (_content_selector) {
            setInterval(this.refresh_fallback, _timer_delay * 1000);
            this.refresh();

            if (_ws_client){
                _ws_client.register('minichat', 'on_connect', this.refresh);
                _ws_client.register('minichat', 'on_message', this.websocket_message_dispatch);
            }
        }
    };

    this.init_post = function () {
        _post_url = $(_form_selector).attr("action");

        $(_button_selector).click(
            function(e) {
                e.preventDefault();
                $(_button_selector).find('span').addClass('fa-spinner fa-spin');
                minichat.post_message();
            }
        );

        this.update_chars_count();
        $(_input_text_selector).change(this.update_chars_count);
        $(_input_text_selector).keyup(this.update_chars_count);
    };

    this.refresh_fallback = function () {
        if (!_ws_client || !_ws_client.isConnected()){
            this.refresh();
        }
    };

    this.websocket_message_dispatch = function (data) {
        switch(data.action) {
            case 'reload_minichat':
                this.refresh();
                break;
        }
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

    this.refresh = function () {
        $.get(_content_url, function (data) {
            var messages = minichat.group_messages(data.results);

            var context = {dates: messages, 'current_username': _username, 'read_date': _read_date};
            $(_content_selector).html(nunjucks.render(_template_url, context));
            _replace_invalid_avatar($(_content_selector));
            _activate_tooltips($(_content_selector));
        });
    };

    this.post_message = function () {
        $.post(_post_url, $(_form_selector).serialize())
            .done(function(data) {
                if (data.substituted) {
                    contrib_message("info", "Votre dernier message est devenu \"<em>"+ data.substituted.text +"</em>\".");
                }
                if (data.anchors.length > 0) {
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
                minichat.update_chars_count();
                minichat.refresh_fallback();
            })
            .fail(function(data) {
                $(_button_selector).find('span').removeClass('fa-spinner fa-spin').addClass('fa-warning');
                minichat_refresh_fallback();
            }
        );
    };

    this.update_chars_count = function () {
        var remaining = $(_input_text_selector).attr("maxlength") - $(_input_text_selector).val().length;
        var plural = "";
        if (remaining > 1) plural = "s";
        $(_input_text_selector).parent().toggleClass("has-warning", remaining == 0);
        $(_remaining_chars_selector).text(remaining + "  caractère"+plural+" restant"+plural);
    };

    return this;
};
