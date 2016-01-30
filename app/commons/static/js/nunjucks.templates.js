(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["commons/contrib_message.html"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "\n<div class=\"alert alert-";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "type"), env.opts.autoescape);
output += " alert-dismissible fade in\" role=\"alert\">\n  <button type=\"button\" class=\"close\" data-dismiss=\"alert\" aria-label=\"Close\"><span aria-hidden=\"true\">&times;</span></button>\n  ";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "message"), env.opts.autoescape);
output += "\n</div>\n";
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
(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["minichat/latests.html"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
output += "\n<div class=\"minichat-content\">\n";
var t_1;
t_1 = "";
frame.set("previousDate", t_1, true);
if(frame.topLevel) {
context.setVariable("previousDate", t_1);
}
if(frame.topLevel) {
context.addExport("previousDate", t_1);
}
output += "\n";
var t_2;
t_2 = false;
frame.set("messageRead", t_2, true);
if(frame.topLevel) {
context.setVariable("messageRead", t_2);
}
if(frame.topLevel) {
context.addExport("messageRead", t_2);
}
frame = frame.push();
var t_5 = runtime.contextOrFrameLookup(context, frame, "results");
if(t_5) {var t_4 = t_5.length;
for(var t_3=0; t_3 < t_5.length; t_3++) {
var t_6 = t_5[t_3];
frame.set("message", t_6);
frame.set("loop.index", t_3 + 1);
frame.set("loop.index0", t_3);
frame.set("loop.revindex", t_4 - t_3);
frame.set("loop.revindex0", t_4 - t_3 - 1);
frame.set("loop.first", t_3 === 0);
frame.set("loop.last", t_3 === t_4 - 1);
frame.set("loop.length", t_4);
if(env.getFilter("naturalDay").call(context, runtime.memberLookup((t_6),"date")) != runtime.contextOrFrameLookup(context, frame, "previousDate")) {
output += "<div class=\"minichat-date\">\n        ";
output += runtime.suppressValue(env.getFilter("naturalDay").call(context, runtime.memberLookup((t_6),"date")), env.opts.autoescape);
output += "\n      </div>";
var t_7;
t_7 = env.getFilter("naturalDay").call(context, runtime.memberLookup((t_6),"date"));
frame.set("previousDate", t_7, true);
if(frame.topLevel) {
context.setVariable("previousDate", t_7);
}
if(frame.topLevel) {
context.addExport("previousDate", t_7);
}
var t_8;
t_8 = true;
frame.set("date_changed", t_8, true);
if(frame.topLevel) {
context.setVariable("date_changed", t_8);
}
if(frame.topLevel) {
context.addExport("date_changed", t_8);
}
;
}
else {
var t_9;
t_9 = false;
frame.set("date_changed", t_9, true);
if(frame.topLevel) {
context.setVariable("date_changed", t_9);
}
if(frame.topLevel) {
context.addExport("date_changed", t_9);
}
;
}
if(runtime.memberLookup((runtime.memberLookup((t_6),"user")),"username") == runtime.contextOrFrameLookup(context, frame, "user")) {
var t_10;
t_10 = true;
frame.set("messageRead", t_10, true);
if(frame.topLevel) {
context.setVariable("messageRead", t_10);
}
if(frame.topLevel) {
context.addExport("messageRead", t_10);
}
;
}
if(runtime.contextOrFrameLookup(context, frame, "date_changed") || runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "results")),runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"index0") - 1)),"user")),"username") != runtime.memberLookup((runtime.memberLookup((t_6),"user")),"username")) {
output += "\n    <div class=\"minichat-message";
if(runtime.memberLookup((runtime.memberLookup((t_6),"user")),"username") == runtime.contextOrFrameLookup(context, frame, "user")) {
output += " self-author";
;
}
else {
output += " other-author";
;
}
output += "\">\n        <a class=\"minichat-user\" href=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((t_6),"user")),"get_absolute_url"), env.opts.autoescape);
output += "\">\n            <img src=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((t_6),"user")),"profile")),"avatar"), env.opts.autoescape);
output += "\" title=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((t_6),"user")),"username"), env.opts.autoescape);
output += "\" class=\"avatar verysmallavatar\"/></a>\n            <div class=\"minichat-text\">";
;
}
output += "\n    <div";
if(!runtime.contextOrFrameLookup(context, frame, "messageRead") && env.getFilter("isAfter").call(context, runtime.memberLookup((t_6),"date"),runtime.contextOrFrameLookup(context, frame, "last_visit"))) {
output += " class=\"new\"";
;
}
else {
if(!runtime.contextOrFrameLookup(context, frame, "messageRead")) {
var t_11;
t_11 = true;
frame.set("messageRead", t_11, true);
if(frame.topLevel) {
context.setVariable("messageRead", t_11);
}
if(frame.topLevel) {
context.addExport("messageRead", t_11);
}
;
}
;
}
if(runtime.memberLookup((t_6),"notification")) {
output += " data-notification=\"";
output += runtime.suppressValue(runtime.memberLookup((t_6),"notification"), env.opts.autoescape);
output += "\"";
;
}
output += ">\n            <span class=\"minichat-time\">";
output += runtime.suppressValue(env.getFilter("time").call(context, runtime.memberLookup((t_6),"date")), env.opts.autoescape);
output += "</span>\n            ";
output += runtime.suppressValue(runtime.memberLookup((t_6),"text"), env.opts.autoescape);
output += "\n            </div>";
if(runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"last") || env.getFilter("naturalDay").call(context, runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "results")),runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"index"))),"date")) != runtime.contextOrFrameLookup(context, frame, "previousDate") || runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "results")),runtime.memberLookup((runtime.contextOrFrameLookup(context, frame, "loop")),"index"))),"user")),"username") != runtime.memberLookup((runtime.memberLookup((t_6),"user")),"username")) {
output += "\n        </div>\n    </div>";
;
}
;
}
}
frame = frame.pop();
output += "\n</div>\n";
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
(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["notifications/button.html"] = (function() {
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
(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["notifications/list.html"] = (function() {
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
output += "\n      <div class=\"next_page small\">\n          <a href=\"javascript:notifications_change_page('";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "next"), env.opts.autoescape);
output += "')\">Suivant <i class=\"fa fa-chevron-right\"></i></a>\n      </div>\n      ";
;
}
output += "\n      ";
if(runtime.contextOrFrameLookup(context, frame, "previous")) {
output += "\n      <div class=\"previous_page small\">\n          <a href=\"javascript:notifications_change_page('";
output += runtime.suppressValue(runtime.contextOrFrameLookup(context, frame, "previous"), env.opts.autoescape);
output += "')\"><i class=\"fa fa-chevron-left\"></i> Précédent</a>\n      </div>\n      ";
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
