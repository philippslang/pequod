from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import django.utils.timezone as future_time_requested



class Request(models.Model):
    requested = models.DateTimeField('date requested', default=future_time_requested.now)
    # this expects and address for a get call that returns a list of accepted queries
    url_analyzer = models.CharField(max_length=250, blank=False)
    base64_audio = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('requested',)


class Response(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    transcript = models.CharField(max_length=200, blank=True, default='na')
    query = models.CharField(max_length=200, blank=True, default='na')

    class Meta:
        ordering = ('request',)