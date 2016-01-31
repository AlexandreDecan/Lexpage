var minichat = function() {
    var _timer_delay = 30000;

    var _content_url;
    var _post_url;
    var _template_url = "minichat/latests.html";

    var _ws_client = ws_client; // Need to be set outside!
    var _username = USERNAME; // Need to be set outside!
    var _last_visit = LAST_VISIT; // Need to be set outside!
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
            setInterval(this.refresh_fallback, _timer_delay);
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

    this.refresh = function () {
        $.get(_content_url, function (data) {

            // Group by date
            var date_groups = _.groupBy(data.results, function (e) {
                return moment(e.date).format("YYYY-MM-DD");
            });

            // Group by author inside each groups
            var ndata = _.map(date_groups, function (messages, date) {
                var last_user = null;
                var groups = [];
                var group;
                for (var i = 0; i < messages.length; i++) {
                    var message = messages[i];
                    if (!last_user || message.user.username != last_user.username) {
                        if (group) {
                            groups.push(group);
                        }

                        last_user = message.user;
                        group = {'user': last_user, 'messages': []};
                    }
                    group.messages.push(message);
                }
                groups.push(group);
                return {'date': date, 'groups': groups};
            });
            var data = {dates: ndata, 'current_username': _username, 'last_visit': _last_visit};
            $(_content_selector).html(nunjucks.render(_template_url, data));
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
}();
