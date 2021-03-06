"""lesson_learned URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import include, url
from rest_framework_swagger.views import get_swagger_view
from rest_framework_swagger import renderers
from rest_framework.permissions import IsAuthenticated, IsAdminUser,AllowAny

from rest_framework.decorators import api_view, renderer_classes, permission_classes
from core import views

class JSONOpenAPIRenderer(renderers.OpenAPIRenderer):
    media_type = 'application/json'

# schema_view = get_swagger_view(title='Main API')

from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer
from rest_framework.decorators import api_view, renderer_classes
from rest_framework import response, schemas


urlpatterns = [
    url(r'^$', views.schema_view),
    url(r'^api/v1/', include('core.urls'), name='core'),
    url(r'^admin/', admin.site.urls)
]
