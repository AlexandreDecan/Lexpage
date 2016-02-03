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
output += "\n<div class=\"minichat-content\">";
frame = frame.push();
var t_3 = runtime.contextOrFrameLookup(context, frame, "dates");
if(t_3) {var t_2 = t_3.length;
for(var t_1=0; t_1 < t_3.length; t_1++) {
var t_4 = t_3[t_1];
frame.set("date_group", t_4);
frame.set("loop.index", t_1 + 1);
frame.set("loop.index0", t_1);
frame.set("loop.revindex", t_2 - t_1);
frame.set("loop.revindex0", t_2 - t_1 - 1);
frame.set("loop.first", t_1 === 0);
frame.set("loop.last", t_1 === t_2 - 1);
frame.set("loop.length", t_2);
output += "<div class=\"minichat-date\">\n    ";
output += runtime.suppressValue(env.getFilter("naturalDay").call(context, runtime.memberLookup((t_4),"date")), env.opts.autoescape);
output += "\n    </div>";
frame = frame.push();
var t_7 = runtime.memberLookup((t_4),"groups");
if(t_7) {var t_6 = t_7.length;
for(var t_5=0; t_5 < t_7.length; t_5++) {
var t_8 = t_7[t_5];
frame.set("group", t_8);
frame.set("loop.index", t_5 + 1);
frame.set("loop.index0", t_5);
frame.set("loop.revindex", t_6 - t_5);
frame.set("loop.revindex0", t_6 - t_5 - 1);
frame.set("loop.first", t_5 === 0);
frame.set("loop.last", t_5 === t_6 - 1);
frame.set("loop.length", t_6);
output += "<div class=\"minichat-message ";
if(runtime.memberLookup((runtime.memberLookup((t_8),"user")),"username") == runtime.contextOrFrameLookup(context, frame, "current_username")) {
output += "self-author";
;
}
else {
output += "other-author";
;
}
output += "\">\n        <a class=\"minichat-user\" href=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((t_8),"user")),"get_absolute_url"), env.opts.autoescape);
output += "\">\n            <img src=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((runtime.memberLookup((t_8),"user")),"profile")),"avatar"), env.opts.autoescape);
output += "\" title=\"";
output += runtime.suppressValue(runtime.memberLookup((runtime.memberLookup((t_8),"user")),"username"), env.opts.autoescape);
output += "\" class=\"avatar verysmallavatar\"/></a>\n            <div class=\"minichat-group\">";
frame = frame.push();
var t_11 = env.getFilter("reverse").call(context, runtime.memberLookup((t_8),"messages"));
if(t_11) {var t_10 = t_11.length;
for(var t_9=0; t_9 < t_11.length; t_9++) {
var t_12 = t_11[t_9];
frame.set("message", t_12);
frame.set("loop.index", t_9 + 1);
frame.set("loop.index0", t_9);
frame.set("loop.revindex", t_10 - t_9);
frame.set("loop.revindex0", t_10 - t_9 - 1);
frame.set("loop.first", t_9 === 0);
frame.set("loop.last", t_9 === t_10 - 1);
frame.set("loop.length", t_10);
output += "<div class=\"minichat-text";
if(runtime.memberLookup((runtime.memberLookup((t_8),"user")),"username") != runtime.contextOrFrameLookup(context, frame, "current_username") && env.getFilter("isAfter").call(context, runtime.memberLookup((t_12),"date"),runtime.contextOrFrameLookup(context, frame, "read_date"))) {
output += " new";
;
}
output += "\">\n                  <span class=\"minichat-time\">";
output += runtime.suppressValue(env.getFilter("time").call(context, runtime.memberLookup((t_12),"date")), env.opts.autoescape);
output += "</span>\n                  <span class=\"minichat-text-content\">";
output += runtime.suppressValue(env.getFilter("highlight").call(context, runtime.memberLookup((t_12),"text"),runtime.contextOrFrameLookup(context, frame, "current_username")), env.opts.autoescape);
output += "</span>\n                </div>";
;
}
}
frame = frame.pop();
output += "</div>\n        </div>";
;
}
}
frame = frame.pop();
;
}
}
frame = frame.pop();
output += "</div>\n";
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
(function() {(window.nunjucksPrecompiled = window.nunjucksPrecompiled || {})["notifications/notifications.html"] = (function() {
function root(env, context, frame, runtime, cb) {
var lineno = null;
var colno = null;
var output = "";
try {
var parentTemplate = null;
if(env.getFilter("length").call(context, runtime.contextOrFrameLookup(context, frame, "data")) > 0) {
output += "\n\n    <a href=\"#\" class=\"dropdown-toggle\" data-toggle=\"dropdown\">\n        <span class=\"badge\"><span class=\"fa fa-bell\"> ";
output += runtime.suppressValue(env.getFilter("length").call(context, runtime.contextOrFrameLookup(context, frame, "data")), env.opts.autoescape);
output += "</span></span>\n    </a>\n    <div class=\"dropdown-menu notification_list\">\n    ";
frame = frame.push();
var t_3 = runtime.contextOrFrameLookup(context, frame, "data");
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
output += "\n       <div id=\"notification_";
output += runtime.suppressValue(runtime.memberLookup((t_4),"id"), env.opts.autoescape);
output += "\" class=\"notification\">\n          <div class=\"notification_icon\">\n            <span class=\"fa fa-lg ";
output += runtime.suppressValue(runtime.memberLookup((t_4),"icon"), env.opts.autoescape);
output += "\"></span>\n          </div>\n          <div class=\"notification_dismiss\">\n              <a class=\"fa fa-times close\" href=\"javascript:app_notifications.dismiss('";
output += runtime.suppressValue(runtime.memberLookup((t_4),"dismiss_url"), env.opts.autoescape);
output += "', 'notification_";
output += runtime.suppressValue(runtime.memberLookup((t_4),"id"), env.opts.autoescape);
output += "');\"></a>\n          </div>\n          <div class=\"notification_title\">\n              ";
if(runtime.memberLookup((t_4),"show_and_dismiss_url")) {
output += "\n              <a href=\"";
output += runtime.suppressValue(runtime.memberLookup((t_4),"show_and_dismiss_url"), env.opts.autoescape);
output += "\">";
output += runtime.suppressValue(runtime.memberLookup((t_4),"title"), env.opts.autoescape);
output += "</a>\n              ";
;
}
else {
output += "\n                  ";
output += runtime.suppressValue(runtime.memberLookup((t_4),"title"), env.opts.autoescape);
output += "\n              ";
;
}
output += "\n          </div>\n          <div class=\"notification_descr\">\n            ";
output += runtime.suppressValue(runtime.memberLookup((t_4),"description"), env.opts.autoescape);
output += "\n            <span class=\"notification_date\">\n              &mdash; ";
output += runtime.suppressValue(env.getFilter("relativeDate").call(context, runtime.memberLookup((t_4),"date")), env.opts.autoescape);
output += "\n            </span>\n          </div>\n        </div>\n    ";
;
}
}
frame = frame.pop();
output += "\n    </div>\n\n";
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
