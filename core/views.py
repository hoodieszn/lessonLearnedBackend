from . import storage
from . import serializers
from . import helpers
from . import models
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

        avg_rating, tutor_reviews = storage.get_tutor_ratings_reviews(tutor)

        result[i].update({
            'courses': [serializers.course_to_dict(course.course) for course in tutored_courses],
            'rating': avg_rating,
            'reviews': [serializers.tutor_review_to_dict(review) for review in tutor_reviews],
        })
    
    return helpers.api_success({'tutors': result})

@helpers.parse_api_json_body
@require_http_methods(["POST"])
def create_tutor_for_degree(request, degree_id, parsed_body=None):

    degree = storage.get_degree_by_id(degree_id)

    if not degree:
        return helpers.api_error("Degree {} not found".format(degree_id), status.HTTP_400_BAD_REQUEST)
    
    user_id = parsed_body.get('user_id', None)
    hourly_rate = parsed_body.get('hourly_rate', None)   
    lat = parsed_body.get('lat', None)
    lon = parsed_body.get('lon', None)
    phone_number = parsed_body.get('phone_number', None)
    courses = parsed_body.get('courses', None)

    if not (user_id and hourly_rate and lat and lon and phone_number and courses):
        return helpers.api_error("Invalid fields: user_id: {}, hourly_rate: {}, lat: {}, lon: {}, phone_number: {}, courses: {}".
                            format(user_id, hourly_rate, lat, lon, phone_number, courses), status.HTTP_400_BAD_REQUEST)

    user = storage.get_user_by_id(user_id)

    if not user:
        return helpers.api_error("Could not find user with id: {}.".format(user_id), status.HTTP_400_BAD_REQUEST)

    existing = storage.get_tutor_information_for_user(user)

    if existing: # Check if if we have already created a tutor profile for this user
        return helpers.api_error("Tutor Information for user already exists.", status.HTTP_400_BAD_REQUEST)

    try:
        tutor_info, tutor_courses = storage.create_tutor_information_for_degree(user, degree, hourly_rate, lat, lon, phone_number, courses)
        
        result = serializers.tutor_to_dict(tutor_info)
        result.update({'courses': courses})

        return helpers.api_success({'tutor': result})

    except Exception as ex:
        return helpers.api_error("Error occured creating TutorInformation and Courses. Exception: {}".
            format(str(ex)), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def get_courses(request, degree_id):

    degree = storage.get_degree_by_id(degree_id)

    if not degree:
        return helpers.api_error("Degree {} not found".format(degree_id), status.HTTP_400_BAD_REQUEST)

    courses_for_degree = storage.get_courses_by_degree(degree)
    return helpers.api_success({'courses': [serializers.course_to_dict(course) for course in courses_for_degree]})

@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def get_schools(request):

    schools = storage.get_schools()
    return helpers.api_success({'schools': [serializers.school_to_dict(school) for school in schools]})

@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def tutor_review_handler(request, tutor_id):
    if request.method == 'GET':
        return get_tutor_reviews(request, int(tutor_id))
    elif request.method == 'POST':
        return add_tutor_review(request, int(tutor_id))

def get_tutor_reviews(request, tutor_id):
    tutor = storage.get_tutor_by_id(tutor_id)
    if not tutor:
        return helpers.api_error("Tutor {} not found".format(tutor_id), status.HTTP_400_BAD_REQUEST)

    reviews = storage.get_tutor_reviews(tutor)
    return helpers.api_success({'reviews': [serializers.review_to_dict(review) for review in reviews]})
    
@helpers.parse_api_json_body
def add_tutor_review(request, tutor_id, parsed_body=None):
    tutor = storage.get_tutor_by_id(tutor_id)

    if not tutor:
        return helpers.api_error("Tutor {} not found".format(tutor_id), status.HTTP_400_BAD_REQUEST)

    comment = parsed_body.get('comment', None)
    rating = parsed_body.get('rating', None)   
    user_id = parsed_body.get('user_id', None)

    if not (comment and rating and user_id):
        return helpers.api_error("Invalid fields: comment: {} rating: {} user_id: {}".format(
                            comment, rating, user_id), status.HTTP_400_BAD_REQUEST)

    user_review_from = storage.get_user_by_id(user_id)

    if not user_review_from:
        return helpers.api_error("Could not find user with id: {}".format(user_id), status.HTTP_400_BAD_REQUEST)

    user_review_to = tutor.user

    if user_review_from.id == user_review_to.id:
        return helpers.api_error("user_id of reviewer must be different from user_id of tutor".
            format(user_id), status.HTTP_400_BAD_REQUEST)

    # Check this user hasnt already left a review for this tutor
    existing_review = storage.get_tutor_reviews(tutor).filter(user=user_review_from)

    if existing_review:
        return helpers.api_error("There already exists review for tutor: {} - with user_id: {} from user: {}".
            format(tutor.id, tutor.user.id, user_id), status.HTTP_400_BAD_REQUEST)

    try:
        new_review = storage.create_review_for_tutor(tutor, comment, rating, user_review_from)
        return helpers.api_success({'review': serializers.review_to_dict(review)})

    except Exception as ex:
        return helpers.api_error("Error occured while creating a TutorReview. Exception: {}".
            format(str(ex)), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
def users_handler(request):
    if request.method == 'GET':
        return get_user(request)
    elif request.method == 'POST':
        return create_user(request)

def get_user(request):
    firebase_id = request.GET.get('firebase_id')

    if not firebase_id:
        return helpers.api_error('pass the firebase_id as a query param', status.HTTP_400_BAD_REQUEST)
    
    user = storage.get_user_from_firebase(firebase_id)

    if not user:
        return helpers.api_error('Could not find a user with firebase_id: {}'.format(firebase_id), status.HTTP_400_BAD_REQUEST)

    result = {'user': serializers.user_to_dict(user)}

    if user.user_type == models.UserType.Tutor.value:
        tutor_info = storage.get_tutor_information_for_user(user)
        
        avg_rating, tutor_reviews = storage.get_tutor_ratings_reviews(tutor_info)

        result['user'].update({'tutor_info': serializers.tutor_to_dict(tutor_info)})
        result['user']['tutor_info'].update({'avg_rating': avg_rating})
        result['user']['tutor_info'].update({'reviews': [serializers.review_to_dict(review) for review in tutor_reviews]})

    return helpers.api_success(result)


@helpers.parse_api_json_body
def create_user(request, parsed_body=None):
    school_id = parsed_body.get('school_id', None)
    user_type = parsed_body.get('user_type', 'student') # Defaults to student
    firebase_id = parsed_body.get('firebase_id', None)

    if not (school_id and firebase_id):
        return helpers.api_error('Invalid fields: school_id: {}, firebase_id: {}'.format(
            school_id, firebase_id), status.HTTP_400_BAD_REQUEST)

    school = storage.get_school_by_id(school_id)

    if not school:
        return helpers.api_error('School with id: {} not found'.format(school_id), status.HTTP_400_BAD_REQUEST)

    try:
        user_type = models.UserType(user_type)
        user_info = storage.create_user_info(school, user_type, firebase_id)

        return helpers.api_success({'user': serializers.user_to_dict(user_info)})

    except Exception as ex:
        return helpers.api_error("Error occured while creating a User. Exception: {}".
            format(str(ex)), status.HTTP_500_INTERNAL_SERVER_ERROR)


