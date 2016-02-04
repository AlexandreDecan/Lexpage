function Notifications(container, url) {
    "use strict";

    this.timer_delay = 10;
    this.last_etag = null;

    this.content_url = url;
    this.template = "notifications/notifications.html";

    this.container_selector = container;
    this.vanilla_title = document.title.replace(/\((\d+)\)/g,'⟨$1⟩'); // Mind "⟨" != "(";

    this.start = function() {
        var _this = this;

        (function loop(){
            _this.refresh();
            setTimeout(loop, _this.timer_delay * 1000);
        })();
    };

    this.reset = function () {
        var _this = this;

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

        $.get(_this.content_url).success(function (data, textStatus, xhr) {
            var etag = xhr.getResponseHeader('ETag');
            if (_this.last_etag != etag) {
                _this.last_etag = etag;
                _this.refresh_content_with(data)
            }
        }).fail(function (data, textStatus, xhr) {
            document.title = _this.vanilla_title;
        });
    };

    this.dismiss = function(url, element) {
        var _this = this;

        $("#" + element + " a.close").addClass("fa-spinner fa-spin");

        $.ajax({url: url, type: 'DELETE'}).success(function () {
            _this.refresh();
        });
    };
}
