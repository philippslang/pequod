from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import RequestFlySerializer, ResponseFlySerializer
from .serializers import RequestSerializer, ResponseSerializer

import models

from interpreter.views import request_impl as interpret

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
        #interpreter_request = interpret(internal_requests.absolute_path(r'/analyzer/queries/'), request_entry.base64_audio)

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
            #matched_query = 'show_plot_pressure'
            interpreter_match = False
            analyzer_request = {}
        else:
            # post the query to analyzer             
            print 'INSPECTOR::views::request: Request for analysis of ',  request_entry.url_rpt        
            analyzer_request = internal_requests.post(r'/analyzer/query/', data = {'query':matched_query, 'url_rpt':request_entry.url_rpt}).json()
        

        # make response result of analyzer query
        response = internal_requests.BAD_VALUE
        info = internal_requests.BAD_VALUE
        items = internal_requests.BAD_VALUE
        url_image = internal_requests.BAD_VALUE

        # everything worked, only response (from analyzer), info is transcript and matched_query, url is set
        # if available and items remain empty
        info = 'Matched your \'' + transcript + '\' to \'' + matched_query + '\''
        try:
            response = analyzer_request['result']            
        except KeyError:
            pass
        try:
            url_image = analyzer_request['url_image']
        except KeyError:           
            pass

        # some feedback on errors
        trascript_feedback = transcript
        if trascript_feedback == internal_requests.BAD_VALUE:
            trascript_feedback = 'empty'

        if not interpreter_match:
            # top level response
            response = 'Unable able to resolve your query.'

            # info
            info ='You: \'' + trascript_feedback + '\'. This is what you can ask for: '

            # items become csv list of supported queries
            supported_queries = internal_requests.get(r'/analyzer/queries/').json()  
            items = []
            for query in supported_queries:
                items += [' '.join(query['query'].split('_'))]
            items = ';'.join(items)
            
        # TODO for now, the response text is the posted rpt url
        #response_entry = request_entry.response_set.create(response=response, transcript=transcript)
        response_entry = models.ResponseFly(response=response, transcript=transcript, url_image=url_image, info=info, items=items)

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

