function Notifications(container, url) {
    "use strict";

    this.timer_delay = 10;
    this.timeout_id = null;
    this.last_etag = null;

    this.content_url = url;
    this.template = "notifications/notifications.html";

    this.container_selector = container;
    this.vanilla_title = document.title.replace(/\((\d+)\)/g,'⟨$1⟩'); // Mind "⟨" != "(";

    this.init = function() {
        var _this = this;

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
        _this.last_etag = null;
        _this.refresh_content_with(null);
    };

    this.refresh_content_with = function (data) {
        var _this = this;

        // Update content
        var template_html = nunjucks.render(_this.template, {'data': data});
        $(_this.container_selector).html(template_html);

        // Disable click event to prevent dropdown closing
        $(_this.container_selector).click(function (e) {
            e.stopPropagation();
        });

        // Allow to show notifications on mouse over
        $(_this.container_selector).hover(function () {
            // Only if navbar is not collapsed
            if (!$(this).closest('.navbar-collapse').hasClass('in'))
                $(this).addClass('open');
        }, function () {
            if (!$(this).closest('.navbar-collapse').hasClass('in'))
                $(this).removeClass('open');
        });

        // Update title
        if (data && data.length > 0)
            document.title = "(" + data.length + ") " + _this.vanilla_title;
        else
            document.title = _this.vanilla_title;
    };

    this.refresh = function () {
        var _this = this;

        // Prevent race condition
        _this.stop_timer();

        $.get(_this.content_url).success(function (data, textStatus, xhr) {
            var etag = xhr.getResponseHeader('ETag');
            if (etag && _this.last_etag != etag) {
                _this.last_etag = etag;
                _this.refresh_content_with(data)
            }
            _this.start_timer();
        }).fail(function (data, textStatus) {
            document.title = _this.vanilla_title;
            contrib_message('danger', 'Une erreur est survenue pendant le chargement des notifications. Veuillez rafraichir la page.');
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
