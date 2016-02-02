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

        app_notifications.refresh_content();
        setInterval(app_notifications.refresh_content, app_notifications.timer_delay * 1000);
    },

    refresh_content: function () {
        $.get(app_notifications.content_url).success(function(data, textStatus, xhr) {
            if (true || xhr.status == 200) {
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
            }
        }).fail(function (data, textStatus, xhr) {
            contrib_message("danger", "Une erreur est survenue pendant le chargement des notifications.");
            document.title = app_notifications.vanilla_title;
        });
    },

    dismiss: function(url, element) {
        $("#" + element + " a.close").addClass("fa-spinner fa-spin");

        $.ajax({url: url, type: 'DELETE'}).success(function () {
            app_notifications.refresh_content();
        }).error(function () {
            contrib_message('danger', 'Une erreur est survenue pendant la suppression de la notification.');
        });
    }
};
