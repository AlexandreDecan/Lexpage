from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.files.base import File, ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible

import sys
import traceback

import slimit
import csscompressor


@deconstructible
class MinifyStatic(StaticFilesStorage):
    def __init__(self, option=None):
        super().__init__()
        self._minify_js = getattr(settings, 'MINIFY_JS', False)
        self._minify_css = getattr(settings, 'MINIFY_CSS', False)
        self._ignored_prefixes = getattr(settings, 'MINIFY_IGNORED_PATHS', [])

    def _save(self, name, original_file):
        if any((name.startswith(prefix) for prefix in self._ignored_prefixes)):
            file = original_file
        elif self._minify_js and name.endswith('.js') and not name.endswith('.min.js'):
            try:
                new_content = slimit.minify(original_file.read().decode('utf-8'), mangle=True, mangle_toplevel=True)
                file = ContentFile(new_content)
            except Exception as e:
                print('Minify JS error for {}:\n{}'.format(name, e), file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                file = original_file

        elif self._minify_css and name.endswith('.css') and not name.endswith('.min.css'):
            try:
                new_content = csscompressor.compress(original_file.read().decode('utf-8'))
                file = ContentFile(new_content)
            except Exception as e:
                print('Minify CSS error for {}:\n{}'.format(name, e), file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                file = original_file
        else:
            file = original_file

        return super()._save(name, file)
