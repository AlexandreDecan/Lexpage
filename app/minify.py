from django.contrib.staticfiles.storage import StaticFilesStorage
from django.core.files.base import ContentFile
from django.conf import settings
from django.utils.deconstruct import deconstructible

from tempfile import NamedTemporaryFile
from yuicompressor import run

import logging

@deconstructible
class MinifyStatic(StaticFilesStorage):
    supported_suffixes = ('js', 'css',)

    def __init__(self, option=None):
        super().__init__()
        self._ignored_prefixes = getattr(settings, 'MINIFY_IGNORED_PATHS', [])

    def minify_enabled(self, kind):
        return getattr(settings, 'MINIFY_%s' % kind.upper(), False)

    def _save(self, name, original_file):
        file = original_file
        if not any((name.startswith(prefix) for prefix in self._ignored_prefixes)):
            for suffix in self.supported_suffixes:
                if self.minify_enabled(suffix) and name.endswith('.%s' % suffix) \
                and not name.endswith('.min.%s' % suffix):
                    try:
                        full_content = NamedTemporaryFile(suffix='.%s' % suffix)
                        full_content.write(original_file.read())
                        full_content.flush()
                        minified_content = NamedTemporaryFile(suffix='.min.%s' % suffix)
                        yuicompress = run(full_content.name, '-o', minified_content.name)
                        assert yuicompress == 0, 'YUI Compressor failed on %s' % name
                        new_content = minified_content.read()
                        file = ContentFile(new_content)
                    except Exception:
                        logging.exception('Minify %s error for %s' % (suffix, name))
                        file = original_file
        return super()._save(name, file)
