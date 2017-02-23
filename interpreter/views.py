from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import RequestSerializer, ResponseSerializer, ResultSerializer
from .serializers import RequestFlySerializer, ResponseFlySerializer

import models

from django.utils import timezone

import requests

from .interpret import interpret

import logging


# TODO implement GET
@api_view(['POST'])
def request(request, format=None):
    """
    Processes the inspection request.
    """

    serializer = RequestFlySerializer(data=request.data)

    if serializer.is_valid():
        request_entry = serializer.create(request.data)

        url_analyzer = request_entry.url_analyzer
        base64_audio = request_entry.base64_audio
        
        response_entry = request_impl(url_analyzer, base64_audio)

        response_serializer = ResponseFlySerializer(response_entry)
        return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def request_impl(url_analyzer, base64_audio):
    # post the query and get json repr of possible matches TODO check 200
    supported_queries = requests.get(url_analyzer)        
    supported_queries = supported_queries.json()              
        
    # do the thing and find the best match 
    iterpretation_results = interpret(base64_audio, supported_queries)

    matched_query = iterpretation_results['matched query']
    transcript = iterpretation_results['transcript']

    # save transcript-query result
    result = models.Result(query=matched_query, transcript=transcript)
    result.save()

    # if matched query empty, needs to be handled at caller level
    return models.ResponseFly(query=matched_query, transcript=transcript)


@api_view(['GET'])
def request_list(request, format=None):
    """
    List all requests processed so far.
    """

    requests = models.Request.objects.all()
    serializer = RequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def requestfly_list(request, format=None):
    """
    List all requests processed so far.
    """

    requests = models.RequestFly.objects.all()
    serializer = RequestFlySerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def response_list(request, format=None):
    """
    List all responses to processed requests so far.
    """

    requests = models.Response.objects.all()
    serializer = ResponseSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def results_list(request, format=None):
    """
    List all results processed so far.
    """

    requests = models.Result.objects.all()
    serializer = ResultSerializer(requests, many=True)
    return Response(serializer.data)

