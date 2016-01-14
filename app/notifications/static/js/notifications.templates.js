(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["/notifications/button.html"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "\n";
if(runtime.contextOrFrameLookup(context, frame, "error")) {
output += "\n    <span class=\"badge\"><span class=\"fa fa-bell-slash\"></span></span>\n";
;
}
else {
if(runtime.contextOrFrameLookup(context, frame, "count") > 0) {
output += "\n    <span class=\"badge\"><span class=\"fa fa-bell\"></span> ";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "count"), env.opts.autoescape);
output += "</span>\n";
;
}
else {
output += "\n    <span class=\"fa fa-navicon\"></span>\n";
;
}
;
}
output += "\n";
if(parentTemplate) {
parentTemplate.rootRenderFunc(env, context, frame, runtime, cb);
} else {
cb(null, output);
}
;
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
return {
root: root
};

})();
})();

(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["/notifications/list.html"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "\n";
output += "\n";
if(runtime.contextOrFrameLookup(context, frame, "error")) {
output += "\n  <div id=\"notification_error\" class=\"notification\">\n    <div class=\"notification_icon\"> \n      <span class=\"fa fa-lg fa-warning\"></span> \n    </div>\n    <div class=\"notification_title\">\n        <strong>Erreur de chargement</strong>\n    </div>\n    <div class=\"notification_descr\">\n      Une erreur est survenue lors du rafraichissement des notifications. Essayez de recharger la page.\n    </div>\n  </div>\n";
;
}
else {
if(env.getFilter("length").call(context, runtime.contextOrFrameLookup(context, frame, "results")) > 0) {
output += "\n  ";
if(runtime.contextOrFrameLookup(context, frame, "next") || runtime.contextOrFrameLookup(context, frame, "previous")) {
output += "\n    <div class=\"notification notification_pagination text-center\">\n      ";
if(runtime.contextOrFrameLookup(context, frame, "next")) {
output += "\n      <div class=\"next_page small\">\n          <a title=\"Suivant\" href=\"javascript:notifications_change_page('";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "next"), env.opts.autoescape);
output += "')\" class=\"change-page\">Suivant <i class=\"fa fa-chevron-right\"></i></a>\n      </div>\n      ";
;
}
output += "\n      ";
if(runtime.contextOrFrameLookup(context, frame, "previous")) {
output += "\n      <div class=\"previous_page small\">\n          <a title=\"Précédent\" href=\"javascript:notifications_change_page('";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "previous"), env.opts.autoescape);
output += "')\" class=\"change-page\"><i class=\"fa fa-chevron-left\"></i> Précédent</a>\n      </div>\n      ";
;
}
output += "\n      <div class=\"text-muted small\">\n          ";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "current_page"), env.opts.autoescape);
output += "/";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "total_pages"), env.opts.autoescape);
output += "\n      </div>\n    </div>\n  ";
;
}
output += "\n  ";
frame = frame.push();
var t_3 = runtime.contextOrFrameLookup(context, frame, "results");
if(t_3) {var t_2 = t_3.length;
for(var t_1=0; t_1 < t_3.length; t_1++) {
var t_4 = t_3[t_1];
frame.set("notification", t_4);
frame.set("loop.index", t_1 + 1);
frame.set("loop.index0", t_1);
frame.set("loop.revindex", t_2 - t_1);
frame.set("loop.revindex0", t_2 - t_1 - 1);
frame.set("loop.first", t_1 === 0);
frame.set("loop.last", t_1 === t_2 - 1);
frame.set("loop.length", t_2);
output += "\n    <div id=\"notification_";
output += runtime.suppressValue(runtime.memberLookup((t_4),"id"), env.opts.autoescape);
output += "\" class=\"notification\">\n      <div class=\"notification_icon\">\n        <span class=\"fa fa-lg ";
output += runtime.suppressValue(runtime.memberLookup((t_4),"icon"), env.opts.autoescape);
output += "\"></span> \n      </div>\n      <div class=\"notification_dismiss\">\n          <a class=\"fa fa-times close\" href=\"javascript:notification_dismiss('";
output += runtime.suppressValue(runtime.memberLookup((t_4),"dismiss_url"), env.opts.autoescape);
output += "', 'notification_";
output += runtime.suppressValue(runtime.memberLookup((t_4),"id"), env.opts.autoescape);
output += "');\"></a>\n      </div>\n      <div class=\"notification_title\"><strong>\n          ";
if(runtime.memberLookup((t_4),"show_and_dismiss_url")) {
output += "\n          <a href=\"";
output += runtime.suppressValue(runtime.memberLookup((t_4),"show_and_dismiss_url"), env.opts.autoescape);
output += "\">";
output += runtime.suppressValue(runtime.memberLookup((t_4),"title"), env.opts.autoescape);
output += "</a>\n          ";
;
}
else {
output += "\n              ";
output += runtime.suppressValue(runtime.memberLookup((t_4),"title"), env.opts.autoescape);
output += "\n          ";
;
}
output += "\n          </strong>\n      </div>\n      <div class=\"notification_descr\">\n        ";
output += runtime.suppressValue(runtime.memberLookup((t_4),"description"), env.opts.autoescape);
output += "\n        <span class=\"notification_date\">\n          &mdash; ";
output += runtime.suppressValue(env.getFilter("relativeDate").call(context, runtime.memberLookup((t_4),"date")), env.opts.autoescape);
output += "\n        </span>\n      </div>\n    </div>\n  ";
;
}
}
frame = frame.pop();
output += "\n";
;
}
;
}
output += "\n";
if(parentTemplate) {
parentTemplate.rootRenderFunc(env, context, frame, runtime, cb);
} else {
cb(null, output);
}
;
} catch (e) {
  cb(runtime.handleError(e, lineno, colno));
}
}
return {
root: root
};

})();
})();

