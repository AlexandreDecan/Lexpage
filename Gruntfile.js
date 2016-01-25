module.exports = function(grunt) {
    grunt.initConfig({
        nunjucks: {
            precompile: {
                baseDir: 'app/',
                src: 'app/*/js_templates/*',
                dest: 'app/commons/static/js/nunjucks.templates.js',
                options: {
                    name: function(filename) {
                        // remove js_templates
                        var path_split = filename.split('/');
                        return path_split[0] + '/' + path_split[2];
                    }
                }
            }
        },
        compass: {
            dist: {
                options: {
                    bundleExec: true,
                    force: true,
                    config: 'app/commons/static/css/config.rb',
                    sassDir: 'app/commons/static/css/',
                    cssDir: 'app/commons/static/css/'
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-contrib-compass');
    grunt.loadTasks('tasks');

    grunt.registerTask('default', ['nunjucks', 'compass']);

}
