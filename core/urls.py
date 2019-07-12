from django.conf.urls import url
import core.views as views

urlpatterns = [
    url(r'^(?P<school_id>[0-9]+)/degrees$', views.get_degrees, name='get_degrees'),
    url(r'^(?P<degree_id>[0-9]+)/tutors', views.tutor_handler, name='get_post_tutors')
]