from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from untitled.celery import app as untitled

__all__ = ('untitled',)