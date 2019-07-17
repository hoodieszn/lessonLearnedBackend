from django.conf.urls import url
import core.views as views

urlpatterns = [
    url(r'^(?P<school_id>[0-9]+)/degrees$', views.get_degrees, name='get_degrees'),
    url(r'^(?P<degree_id>[0-9]+)/postings', views.postings_handler, name='tutor_postings'),
    url(r'^(?P<degree_id>[0-9]+)/courses$', views.get_courses, name='get_courses_for_degree'),
    url(r'^contacts$', views.handle_tutor_contacts, name='get_create_tutor_contacts'),
    url(r'^schools$', views.get_schools, name='get_schools'),
    url(r'^(?P<tutor_id>[0-9]+)/reviews$', views.tutor_review_handler, name='get_post_tutor_reviews'),
    url(r'^users$', views.users_handler, name='get_create_users'),
    url(r'^users/(?P<user_id>[0-9]+)$', views.get_user_by_id, name='get_user_by_id'),
]