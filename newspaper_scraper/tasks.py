from __future__ import absolute_import, unicode_literals
from celery import shared_task
import logging
from django.utils import timezone
logger = logging.getLogger("scraper_logger")


@shared_task
def task_push_to_sheets():
    from .import_from_pandas import push_to_sheets, query
    push_to_sheets(query)
    logger.info("[{}] Custom query have been pushed to Sheets.".format(timezone.now()))

@shared_task
def add(x, y):
    return x + y
