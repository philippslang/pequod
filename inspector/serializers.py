from rest_framework import serializers
from .models import Request, Response, RequestFly, ResponseFly


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('requested', 'url_rpt', 'base64_audio')


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('request', 'response', 'transcript',)


class RequestFlySerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return RequestFly(**validated_data)

    class Meta:
        model = RequestFly
        fields = ('url_rpt', 'base64_audio')


class ResponseFlySerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return ResponseFly(**validated_data)

    class Meta:
        model = ResponseFly
        fields = ('response', 'transcript',)