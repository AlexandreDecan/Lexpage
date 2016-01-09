var env = nunjucks.configure({ autoescape: false });

env.addFilter('relativeDate', function(val, cb) {
    return moment(val).fromNow();
}, true);

