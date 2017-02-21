from __future__ import unicode_literals

from django.db import models

from .queries import SUPPORTED_QUERIES

# Create your models here.


# TODO make these unique and always instantiated for all SUPPORTED_QUERIES
class SupportedQuery(models.Model):
    query = models.CharField(choices=SUPPORTED_QUERIES, max_length=200, blank=False)

    class Meta:
        ordering = ('query',)


class Query(models.Model):
    query = models.CharField(choices=SUPPORTED_QUERIES, max_length=200, blank=False)
    url_rpt = models.CharField(max_length=200, blank=False)

    class Meta:
        ordering = ('url_rpt',)


# TODO instead of a formatted string, we could add a result type etc.. to let receiver
# take care of means of displying, ie number, text, percentage etc...
class Result(models.Model):
    query = models.ForeignKey(Query, on_delete=models.CASCADE)
    result = models.CharField(max_length=200, blank=True, default='none')
    url_image = models.CharField(max_length=250, blank=True, default='na')


    class Meta:
        ordering = ('query',)