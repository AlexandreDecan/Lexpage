function Minichat(username, last_visit, container_selector, form_selector, content_url) {
    "use strict";

    this.timer_delay = (username && username != "") ? 10 : 30;
    this.split_delay = 5 * 60;
    this.last_etag = null;

    this.username = username;
    this.read_date = last_visit;

    this.content_url = content_url;
    this.template = "minichat/latests.html"

    this.container_selector = container_selector;
    this.form_selector = form_selector;

    this.start = function() {
        var _this = this;

        _this._button_selector = form_selector + " button[type='submit']";
        _this._input_text_selector = form_selector + " input[type='text']";
        _this._remaining_chars_selector = form_selector + " .minichat-remainingChars";

        $(_this._button_selector).click(function(e) {
            e.preventDefault();
            $(_this._button_selector).find('span').addClass('fa-spinner fa-spin');
            _this.post_message();
        });

        _this.update_chars_count();
        $(_this._input_text_selector).change(app_minichat.update_chars_count);
        $(_this._input_text_selector).keyup(app_minichat.update_chars_count);

        (function loop(){
            _this.refresh();
            setTimeout(loop, _this.timer_delay * 1000);
        })();
    };


    this.group_messages = function(messages) {
        var _this = this;

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
    };

    this.reset = function() {
        var _this = this;

        _this.last_etag = null;
        _this.refresh_content_with([]);
    };

    this.refresh_content_with = function(data) {
        var _this = this;

        var messages = _this.group_messages(data);

            var context = {dates: messages, 'current_username': _this.username, 'read_date': _this.read_date};
            $(_this.container_selector).html(nunjucks.render(_this.template, context));
            replace_invalid_avatar($(_this.container_selector));
            activate_tooltips($(_this.container_selector));
    };

    this.refresh = function () {
        var _this = this;

        $.get(_this.content_url).success(function (data, textStatus, xhr) {
            var etag = xhr.getResponseHeader('ETag');
            if (_this.last_etag != etag) {
                _this.last_etag = etag;
                _this.refresh_content_with(data.results)
            }
        });
    };

    this.post_message = function () {
        var _this = this;

        $.post($(_this.form_selector).attr("action"), $(_this.form_selector).serialize())
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
                $(_this._button_selector).find('span').removeClass('fa-spinner fa-spin fa-warning btn-warning');
                $(_this._input_text_selector).val("");
                _this.update_chars_count();
                _this.refresh();
            })
            .fail(function() {
                    $(_this._button_selector).find('span').removeClass('fa-spinner fa-spin').addClass('fa-warning');
                    _this.refresh();
                }
            );
    };

    this.update_chars_count = function () {
        var _this = this;

        var remaining = $(_this._input_text_selector).attr("maxlength") - $(_this._input_text_selector).val().length;
        var plural;
        if (remaining > 1) plural = "s"; else plural = "";

        $(_this._input_text_selector).parent().toggleClass("has-warning", remaining == 0);
        $(_this._remaining_chars_selector).text(remaining + "  caractère"+plural+" restant"+plural);
    };
}

