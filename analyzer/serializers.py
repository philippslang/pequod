from rest_framework import serializers
from .models import SupportedQuery, Query, Result


class SupportedQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportedQuery
        fields = ('query',)


class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('query', 'url_rpt')


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('query', 'result', 'url_image',)