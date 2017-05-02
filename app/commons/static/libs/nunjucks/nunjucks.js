var env = nunjucks.configure({ autoescape: false });

env.addFilter('relativeDate', function(val) {
    return moment(val).fromNow();
}, true);

env.addFilter('time', function(val) {
    return moment(val).format('HH[h]mm');
}, true);

env.addFilter('isAfter', function(val, ref) {
    return moment(val).isAfter(ref);
}, true);

env.addFilter('highlightAnchor', function(val, user) {
    if (user == ""){ // anonymous user
        return val;
    } else {
        var user_regexp = new RegExp("(@" + user + ")(\\b)", "g");
        return val.replace(user_regexp, "<span class=\"highlight\">$1</span>");
    };
}, true);

env.addFilter('naturalDay', function(val) {
    return moment(val).calendar(null, {
            sameDay: '[aujourd\'hui]',
            nextDay: '[demain]',
            nextWeek: 'dddd',
            lastDay: '[hier]',
            lastWeek: 'dddd D MMM',
            sameElse: 'dddd D MMM'
    });
}, true);

