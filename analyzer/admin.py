from django.contrib import admin

# Register your models here.


from .models import SupportedQuery

admin.site.register(SupportedQuery)