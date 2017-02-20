# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.http import HttpResponse
from django.template import loader
from django.core.files.storage import FileSystemStorage

from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Report
from .serializers import ReportSerializer

from google.cloud import storage


DEFAULT_RPT_FNAME = 'current.PRT'
PRT_BUCKET = 'pequod'


def index(request):
    template = loader.get_template('ui/index.html')
    context = {}
    return HttpResponse(template.render(context, request))




# TODO can I use the decorator here?
# deprecate when we figure out the model based solution
# for now, we only store one prt file under the same name
@api_view(['POST'])
def rpt_upload_plain(request):
    key_name = 'rptfile'

    if request.FILES[key_name]:
        #print 'I am in UI'
        # TODO make this a  MemoryFileUploadHandler or TemporaryFileUploadHandler 

        # https://googlecloudplatform.github.io/google-cloud-python/stable/storage-client.html

        # TODO fetch an app wide available encryption key
        client = storage.Client()
        bucket_name = PRT_BUCKET
        #bucket = client.get_bucket(bucket_name)
        
        
        # this is an https://docs.djangoproject.com/en/1.10/ref/files/uploads/#django.core.files.uploadedfile.UploadedFile
        #rpt_file = request.FILES[key_name]

        #blob_name = rpt_file.name
        #blob = storage.Blob(blob_name, bucket)

        # TODO for proper type/encoding, check for good response

        # TODO transfer in chunks or create a handler as described above
        #blob.upload_from_string(rpt_file.read(), content_type='text/plain', client=client)
        
        # TODO do we neeed this if we only access app wide?
        #blob.make_public()

        #report = Report(public_url=blob.public_url, file_name=blob_name)
        report = Report(public_url="", file_name="")
        report.save()
        report_serializer = ReportSerializer(report)

        # TODO return the uri hiere
        return Response(report_serializer.data)
        return HttpResponse(status=202)

    return HttpResponse(status=404)