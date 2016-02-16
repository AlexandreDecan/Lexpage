function Notifications(container, button_container, url) {
    "use strict";

    this.timer_delay = 10;
    this.timeout_id = null;
    this.last_hash = null;

    this.content_url = url;
    this.template = "notifications/notifications.html";
    this.template_button = "notifications/button.html";

    this.container_selector = container;
    this.button_container_selector = button_container;
    this.vanilla_title = document.title.replace(/\((\d+)\)/g,'⟨$1⟩'); // Mind "⟨" != "(";

    this.init = function() {
        var _this = this;

        // Disable click event to prevent dropdown closing
        $(_this.container_selector).click(function (e) {
            e.stopPropagation();
        });

        // Allow to show notifications on mouse over
        $(_this.container_selector).hover(function () {
            // Only if navbar is not collapsed
            //if (!$(this).closest('.navbar-collapse').hasClass('in'))
                $(this).addClass('open');
        }, function () {
            //if (!$(this).closest('.navbar-collapse').hasClass('in'))
                $(this).removeClass('open');
        });

        _this.refresh();
    };

    this.stop_timer = function() {
        var _this = this;

        if (_this.timeout_id) {
            clearTimeout(_this.timeout_id);
            _this.timeout_id = null;
        }
    };

    this.start_timer = function() {
        var _this = this;

        _this.stop_timer();
        _this.timeout_id = setTimeout(function() { _this.refresh(); }, _this.timer_delay * 1000);
    };

    this.reset = function () {
        var _this = this;

        _this.start_timer();
        _this.last_hash = null;
        _this.refresh_content_with({data: null});
    };

    this.refresh_content_with = function (content) {
        var _this = this;

        // Update content
        var template_html = nunjucks.render(_this.template, content);
        $(_this.container_selector).html(template_html);

        var template_button_html = nunjucks.render(_this.template_button, content);
        $(_this.button_container_selector).html(template_button_html);

        if (content && content.data && content.data.length > 0) {
            // Update title
            document.title = "(" + content.data.length + ") " + _this.vanilla_title;
        } else {
            document.title = _this.vanilla_title;
            // Close container, if needed
            $(_this.container_selector).removeClass('open');
        }
    };

    this.refresh = function () {
        var _this = this;

        // Prevent race condition
        _this.stop_timer();

        $.get(_this.content_url + "?hash=" + _this.last_hash).success(function (data, textStatus, xhr) {
            if (data && (!_this.last_hash || _this.last_hash != data.hash)) {
                _this.last_hash = data.hash;
                _this.refresh_content_with({data: data.results})
            }
            _this.start_timer();
        }).fail(function (data, textStatus) {
            document.title = _this.vanilla_title;
            _this.refresh_content_with({data: null, error: true});
            // contrib_message('danger', 'Une erreur est survenue pendant le chargement des notifications. Veuillez rafraichir la page.');
            console.log(data);
            console.log(textStatus);
        });
    };

    this.dismiss = function(url, element) {
        var _this = this;

        // Prevent race condition
        _this.stop_timer();

        $("#" + element + " a.close").addClass("fa-spinner fa-spin");
        $.ajax({url: url, type: 'DELETE'}).success(function () {
            _this.refresh();
        }).fail(function (data, textStatus) {
            contrib_message('danger', 'Une erreur est survenue pendant la suppression de la notification.');
            console.log(data);
            console.log(textStatus);
            _this.refresh();
        });
    };
}
