from rest_framework import serializers
from .models import Request, Response, Result
from .models import RequestFly, ResponseFly


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ('requested', 'base64_audio', 'url_analyzer',)


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ('query', 'transcript')


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = ('resulted', 'query', 'transcript')


class RequestFlySerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        rf = RequestFly(**validated_data)
        rf.url_analyzer  =rf.url_analyzer[0]
        rf.base64_audio  =rf.base64_audio[0]
        return rf

    class Meta:
        model = RequestFly
        fields = ('url_analyzer', 'base64_audio', )


class ResponseFlySerializer(serializers.ModelSerializer):

    class Meta:
        model = ResponseFly
        fields = ('transcript', 'query',)