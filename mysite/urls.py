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

from django.conf.urls import include, url
from django.contrib import admin

from django.contrib.auth.models import User
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^', include('ui.urls')),
    url(r'^analyzer/', include('analyzer.urls')),
    url(r'^inspector/', include('inspector.urls')),
    url(r'^interpreter/', include('interpreter.urls')),
    url(r'^meister/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

