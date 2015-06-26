// Because MS sucks...
if (navigator.userAgent.match(/IEMobile\/10\.0/)) {
  var msViewportStyle = document.createElement('style')
  msViewportStyle.appendChild(
    document.createTextNode(
      '@-ms-viewport{width:auto!important}'
    )
  )
  document.querySelector('head').appendChild(msViewportStyle)
}



$(document).ready(function() {
    // Replace empty or invalid avatar. 
    replace_invalid_avatar($("body"));

    // Activate tooltips
    activate_tooltips($("body"));

    // Open navbar menu when hover, only if navbar is not collapsed
    $('#navbarA-collapse .dropdown-toggle').closest('li').hover(function(){
        if (! $('#navbarA-collapse').hasClass('in'))                
            $(this).addClass('open');
    }, function() {
        if (! $('#navbarA-collapse').hasClass('in')) 
            $(this).removeClass('open');
    });

    // Confirm dialog    
    $('.confirm-action').click(function (e) {
        e.preventDefault();
        $('#confirm-action').modal('show');
        $('#confirm-action #confirm-action-yes').attr('href', $(this).attr('href'));
    });

    // OEmbed-ed elements
    refresh_oembed($("body"));

    // Init notifications if any
    notification_initialize();

    // Auto-hide navbar on scroll
    $(".navbar-fixed-top").autoHidingNavbar({showOnBottom: false});
});


function refresh_oembed(target) {
    target.find('a.oembed').oembed(null, {maxHeight:"400"});
    target.find('a.embedly').each(function (i, e) {
        e = $(e);
        var README = "Please, do NOT use this API key. You can get one too for free on http://embed.ly !";
        var url = "http://api.embed.ly/1/extract?key=396f02e230724c218db720b2dd2daed0&url="+e.attr('href');
        $.ajax(url).done(function (r) {
            if (r['images'] && r['images'][0] && r['images'][0]['url']) {
                e.append('<img src="'+r['images'][0]['url']+'"/>');
            } else {
                e.replaceWith('');
            }
        });
    });

}

function activate_tooltips(target) {
    if (!Modernizr.touch){
        $(target).find("[data-toggle='tooltip']").tooltip();
        $(target).find(".avatar[title]").tooltip();    
    }
}

function replace_invalid_avatar(inside) {
    // Replace non-existent or empty avatars
    $(inside).find("img.avatar[src='']").each(function() {
      $(this).attr("src", URL_PREFIX + "/static/images/avatars/default.png");
    });
    $(inside).find("img.avatar").error(function () {  
     $(this).unbind("error").attr("src", URL_PREFIX + "/static/images/avatars/erreur404.png"); });     
}


function notification_initialize() {
    $(".notification_list .notification_dismiss a.close").click(function (e) {
        e.stopPropagation(); // Prevent dropdown to close
    });
}

function notification_dismiss(url, target) {
    // Disable click propagation (to keep dropdown opened)
    function done(data) {
        // Dismiss target
        $("#"+target).fadeTo(250, 0.35);
        // Remove link (to avoid 404)
        $("#"+target+" a").click(function (e) { e.preventDefault(); e.stopPropagation(); });
        $("#"+target+" a.close").removeClass("fa-spinner fa-spin");
    }
    $("#"+target+" a.close").addClass("fa-spinner fa-spin");
    $.get(url).done(done);
}
