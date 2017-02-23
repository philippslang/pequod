from __future__ import unicode_literals

from django.db import models
from django.utils import timezone
import django.utils.timezone as future_time_requested
# Create your models here.

from mysite.dispatch import BAD_VALUE


class Request(models.Model):
    requested = models.DateTimeField('date requested', default=future_time_requested.now)
    url_rpt = models.CharField(max_length=200, blank=True, default=BAD_VALUE)
    base64_audio = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('requested',)

class Response(models.Model):
    request = models.ForeignKey(Request, on_delete=models.CASCADE)
    response = models.CharField(max_length=200, blank=True, default=BAD_VALUE)
    transcript = models.CharField(max_length=200, blank=True, default=BAD_VALUE)
    info = models.CharField(max_length=200, blank=True, default=BAD_VALUE)
    items = models.CharField(max_length=200, blank=True, default=BAD_VALUE)

    class Meta:
        ordering = ('request',)


class RequestFly(models.Model):
    url_rpt = models.CharField(max_length=200, blank=True, default=BAD_VALUE)
    base64_audio = models.TextField(blank=True, default='')


class ResponseFly(models.Model):
    response = models.CharField(max_length=200, blank=True, default=BAD_VALUE)
    transcript = models.CharField(max_length=200, blank=True, default=BAD_VALUE)
    url_image = models.CharField(max_length=250, blank=True, default=BAD_VALUE)
    info = models.CharField(max_length=200, blank=True, default=BAD_VALUE)
    items = models.CharField(max_length=200, blank=True, default=BAD_VALUE)