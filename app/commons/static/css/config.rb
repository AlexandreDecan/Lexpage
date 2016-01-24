# Require any additional compass plugins here.

# Set this to the root of your project when deployed:
http_path = "/"
css_dir = "../css"
sass_dir = ""
images_dir = "../images"
# javascripts_dir = "javascripts"
environment = :production

if environment == :production
  output_style = :expanded # This will be minified by `collectstatic`. See app/minify.py.
  line_comments = false
else
  output_style = :expanded
end

# You can select your preferred output style here (can be overridden via the command line):
# output_style = :expanded or :nested or :compact or :compressed

# To enable relative paths to assets via compass helper functions. Uncomment:
# relative_assets = true

# To disable debugging comments that display the original location of your selectors. Uncomment:
# line_comments = false
