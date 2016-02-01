app_notifications = function (ws_client) {
    var _timer_delay = 30;
    var _ws_client = ws_client;

    var _content_url;
    var _template = "notifications/notifications.html";

    var _container_selector;

    var _vanilla_title = document.title.replace(/\((\d+)\)/g,'⟨$1⟩'); // Mind "⟨" != "("

    var app = this;

    this.init_display = function (container, url) {
        _container_selector = container;
        _content_url = url;

        // Register if available
        if (_ws_client) {
            ws_client.register('notifications', 'on_message', function(data) {
                if (data.action == "update_counter") {
                    app.refresh_content();
                }
            });
        }

        setInterval(function () {
            // If not connected, use fallback
            if (!_ws_client || !_ws_client.isConnected()){
                app.refresh_content();
            }
        }, _timer_delay * 1000);

        this.refresh_content();
    };

    this.refresh_content = function () {
        $.get(_content_url, function(data) {
            // Update content
            var template_html = nunjucks.render(_template, {'data':data});
            $(_container_selector).html(template_html);

            // Disable click event to prevent dropdown closing
            $(_container_selector).click(function(e) {e.stopPropagation(); });

            // Allow to show notifications on mouse over
            $(_container_selector).hover(function () {
                // Only if navbar is not collapsed
                if (!$(this).closest('.navbar-collapse').hasClass('in'))
                    $(this).addClass('open');
            }, function() {
                if (!$(this).closest('.navbar-collapse').hasClass('in'))
                    $(this).removeClass('open');
            });

            // Update title
            if (data && data.length > 0)
                document.title = "("+data.length+") "+_vanilla_title;
            else
                document.title = _vanilla_title;
        }).error(function () {
            contrib_message("danger", "Une erreur est survenue pendant le chargement des notifications.");
            document.title = _vanilla_title;
        });
    };

    this.dismiss = function(url, element) {
        // Disable click event to prevent dropdown closing
        $("#" + element + " a.close").addClass("fa-spinner fa-spin");
        $.ajax({url: url, type: 'DELETE'}).done(function (data) {
            app.refresh_content();
        });
    }

    return this;
};