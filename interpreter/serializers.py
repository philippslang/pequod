from rest_framework import serializers
from .models import Request, Response


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('requested', 'base64_audio', 'url_analyzer',)


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('query', 'transcript')