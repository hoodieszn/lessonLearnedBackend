from django.conf.urls import url
import core.views as views

urlpatterns = [
    url(r'^degrees/(?P<school_id>[0-9]+)$', views.get_degrees, name='get_degrees')
]
