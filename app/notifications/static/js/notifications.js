"use strict";

var app_notifications = {
    timer_delay: 10,

    content_url: null,
    template: "notifications/notifications.html",

    container_selector: null,
    vanilla_title: null,

    init: function (container, url) {
        app_notifications.vanilla_title = document.title.replace(/\((\d+)\)/g,'⟨$1⟩'); // Mind "⟨" != "("
        app_notifications.container_selector = container;
        app_notifications.content_url = url;

        (function loop(){
            app_notifications.refresh();
            setTimeout(loop, app_notifications.timer_delay * 1000);
        })();
    },

    reset: function () {
        app_notifications.refresh_content_with(null);
    },

    refresh_content_with: function (data) {
        // Update content
        var template_html = nunjucks.render(app_notifications.template, {'data': data});
        $(app_notifications.container_selector).html(template_html);

        // Disable click event to prevent dropdown closing
        $(app_notifications.container_selector).click(function (e) {
            e.stopPropagation();
        });

        // Allow to show notifications on mouse over
        $(app_notifications.container_selector).hover(function () {
            // Only if navbar is not collapsed
            if (!$(this).closest('.navbar-collapse').hasClass('in'))
                $(this).addClass('open');
        }, function () {
            if (!$(this).closest('.navbar-collapse').hasClass('in'))
                $(this).removeClass('open');
        });

        // Update title
        if (data && data.length > 0)
            document.title = "(" + data.length + ") " + app_notifications.vanilla_title;
        else
            document.title = app_notifications.vanilla_title;
    },

    refresh: function () {
        $.get(app_notifications.content_url).success(function(data, textStatus, xhr) {
                app_notifications.refresh_content_with(data);
        }).fail(function (data, textStatus, xhr) {
            document.title = app_notifications.vanilla_title;
        });
    },

    dismiss: function(url, element) {
        $("#" + element + " a.close").addClass("fa-spinner fa-spin");

        $.ajax({url: url, type: 'DELETE'}).success(function () {
            app_notifications.refresh();
        });
    }
};
