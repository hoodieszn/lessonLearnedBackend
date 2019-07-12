from . import storage
from . import serializers
from . import helpers
from rest_framework import status
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes


# need to implement token auth or something

@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@require_GET
def get_degrees(request, school_id):
    # Return All the degrees for a given school
    degrees = storage.get_degrees(school_id)
    return helpers.api_success({'degrees': [serializers.degree_to_dict(deg) for deg in degrees]})


@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def tutor_handler(request, degree_id):
    if request.method == 'GET':
        return get_tutors(request, degree_id)
    elif request.method == 'POST':
        return create_tutor_for_degree(request, degree_id)


def get_tutors(request, degree):
    tutors = storage.get_tutors(degree)
    result = [serializers.tutor_to_dict(tutor) for tutor in tutors]
    course_code = request.GET.get('code')
    
    for i,tutor in enumerate(tutors):
        tutored_courses = storage.get_courses_per_tutor(tutor)

        # Filtering using code
        if course_code and not any(tutored_course.course.id == int(course_code) for tutored_course in tutored_courses):
            del result[i]
            continue

        avg_rating, tutor_ratings = storage.get_tutor_reviews(tutor)

        result[i].update({
            'courses': [serializers.course_to_dict(course.course) for course in tutored_courses],
            'rating': avg_rating,
            'reviews': [serializers.tutor_review_to_dict(review) for review in tutor_ratings],
        })
    
    return helpers.api_success({'tutors': result})


# def create_tutor_for_degree(request, degree_id):
