from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import SupportedQuery
from .serializers import SupportedQuerySerializer, QuerySerializer, ResultSerializer
from .analysis import analyze

@api_view(['GET', 'POST'])
def supported_queries(request, format=None):
    """
    List all supported queries.
    """

    if request.method == 'GET':
        queries = SupportedQuery.objects.all()
        serializer = SupportedQuerySerializer(queries, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = SupportedQuerySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# TODO implement GET
@api_view(['POST'])
def query(request, format=None):
    """
    Processes a query.
    """

    serializer = QuerySerializer(data=request.data)

    if serializer.is_valid():
        query_entry = serializer.save()

        print 'ANALYZER::views::query: Request for ',  query_entry.query

        # TODO for now, the result text is dummy
        result = 'Inspection ' + query_entry.query + ' not possible for ' + query_entry.url_rpt + '.'
        result, url_image = analyze(query_entry.query, query_entry.url_rpt)

        result_entry = query_entry.result_set.create(result=result, url_image=url_image)

        result_serializer = ResultSerializer(result_entry)
        return Response(result_serializer.data, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
