from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import RequestFlySerializer, ResponseFlySerializer
from .serializers import RequestSerializer, ResponseSerializer

import models

from django.utils import timezone

import mysite.dispatch as internal_requests

import requests

import json
import uuid


# TODO implement GET
@api_view(['POST'])
def request(request, format=None):
    """
    Processes the inspection request.
    """

    #serializer = RequestSerializer(data=request.data)
    serializer = RequestFlySerializer(data=request.data)
    

    if serializer.is_valid():
        #request_entry = serializer.save()        
        request_entry = serializer.create(request.data)        
    
        
        # post to interpreter, and the use receiver query here
        interpreter_request = internal_requests.post(r'/interpreter/request/', data = {'base64_audio':request_entry.base64_audio, 'url_analyzer':internal_requests.absolute_path(r'/analyzer/queries/'), 'cachekiller':str(uuid.uuid1())})
        try:
            interpreter_request = interpreter_request.json()
            transcript = interpreter_request['transcript']
            matched_query = interpreter_request['query']
        except:
            transcript = internal_requests.BAD_VALUE
            matched_query = internal_requests.BAD_VALUE


        # default query for now in case of bad interpreter result
        interpreter_match = True
        if matched_query == internal_requests.BAD_VALUE:
            matched_query = 'show_plot_pressure'
            interpreter_match = False

        # check for inspector errors, ie empty query

        # post the query to analyzer     
        
        print 'INSPECTOR::views::request: Request for analysis of ',  request_entry.url_rpt
        
        analyzer_request = internal_requests.post(r'/analyzer/query/', data = {'query':matched_query, 'url_rpt':request_entry.url_rpt})
        
        # TODO check 202
        # make response result of analyzer query
        analyzer_request = analyzer_request.json()
        try:
            response = analyzer_request['result']
        except KeyError:
            response = 'Analyzer could not resolve query ' + matched_query
        try:
            url_image = analyzer_request['url_image']
        except KeyError:
            # TODO make empty            
            url_image = internal_requests.BAD_VALUE

        if not interpreter_match:
            # TODO list supported queries
            response_queries = ''
            supported_queries = internal_requests.get(r'/analyzer/queries/')   
            supported_queries = supported_queries.json() 
            for query in supported_queries:
                response_queries += ' '.join(query['query'].split('_')) + ', '
            displayed_transcript = transcript
            if displayed_transcript == internal_requests.BAD_VALUE:
                displayed_transcript = 'empty'
            response = 'Wasn\'t able to resolve your query: \'' + displayed_transcript +'\'. This is what you can ask for: ' \
                       + response_queries + '.    Let me show you a pressure summary instead:'

        # TODO for now, the response text is the posted rpt url
        #response_entry = request_entry.response_set.create(response=response, transcript=transcript)
        response_entry = models.ResponseFly(response=response, transcript=transcript, url_image=url_image)

        # here we call a function that modifies  response_entry - it wil have access to request_entry

        response_serializer = ResponseFlySerializer(response_entry)
        return Response(response_serializer.data, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def request_list(request):
    """
    List all requests processed so far.
    """

    requests = models.Request.objects.all()
    serializer = RequestSerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def requestfly_list(request):
    """
    List all temp requests processed so far, should be empty.
    """

    requests = models.RequestFly.objects.all()
    serializer = RequestFlySerializer(requests, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def response_list(request):
    """
    List all responses to processed requests so far.
    """

    requests = models.Response.objects.all()
    serializer = ResponseSerializer(requests, many=True)
    return Response(serializer.data)

