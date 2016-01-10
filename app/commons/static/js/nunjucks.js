var env = nunjucks.configure({ autoescape: false });

env.addFilter('relativeDate', function(val, cb) {
    return moment(val).fromNow();
}, true);

env.addFilter('time', function(val, cb) {
    return moment(val).format('HH[h]mm');
}, true);

env.addFilter('naturalDay', function(val, cb) {
    return moment(val).calendar(null, {
            sameDay: '[aujourd\'hui]',
            nextDay: '[demain]',
            nextWeek: 'dddd',
            lastDay: '[hier]',
            lastWeek: 'dddd D MMM',
            sameElse: 'dddd D MMM'
    });
}, true);

