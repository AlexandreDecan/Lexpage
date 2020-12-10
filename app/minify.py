from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible

from css_html_js_minify import css_minify, js_minify

import logging


@deconstructible
class MinifyStatic(StaticFilesStorage):

    def __init__(self, option=None):
        super().__init__()
        self._ignored_prefixes = getattr(settings, 'MINIFY_IGNORED_PATHS', [])

    def minify_enabled(self, kind):
        return getattr(settings, 'MINIFY_%s' % kind.upper(), False)

    def _save(self, name, original_file):
        file = original_file
        if not any((name.startswith(prefix) for prefix in self._ignored_prefixes)):
            if name.endswith('.js') and not name.endswith('.min.js') and self.minify_enabled('js'):
                func = js_minify
            elif name.endswith('.css') and not name.endswith('.min.css') and self.minify_enabled('css'):
                func = css_minify
            else:
                func = None

            if func is not None:
                try:
                    content = original_file.read().decode()
                    minified = func(content)
                    file = ContentFile(minified)
                except Exception:  # pragma: no cover
                    logging.exception('Minify error for %s' % name,)
                    file = original_file
        return super()._save(name, file)
