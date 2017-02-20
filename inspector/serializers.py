from rest_framework import serializers
from .models import Request, Response


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('requested', 'url_rpt', 'base64_audio')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('request', 'response', 'transcript',)