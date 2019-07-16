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
def postings_handler(request, degree_id):
    if request.method == 'GET':
        return get_postings(request, degree_id)
    elif request.method == 'POST':
        return create_tutor_posting(request, degree_id)


def get_postings(request, degree):
    tutor_postings = storage.get_tutor_posting_for_degree(degree)

    result = [serializers.tutor_posting_to_dict(posting) for posting in tutor_postings]
    course_code = request.GET.get('code')
    
    for i,posting in enumerate(tutor_postings):
        tutored_courses = storage.get_courses_per_posting(posting)

        # Filtering using code
        if course_code and not any(tutored_course.course.id == int(course_code) for tutored_course in tutored_courses):
            del result[i]
            continue

        avg_rating, tutor_reviews = storage.get_tutor_ratings_reviews(posting.tutor)

        result[i].update({
            'courses': [serializers.course_to_dict(course.course) for course in tutored_courses],
            # 'rating': avg_rating,
            # 'reviews': [serializers.tutor_review_to_dict(review) for review in tutor_reviews],
        })
    
    return helpers.api_success({'tutorPostings': result})

@helpers.parse_api_json_body
@require_http_methods(["POST"])
def create_tutor_posting(request, degree_id, parsed_body=None):

    degree = storage.get_degree_by_id(degree_id)

    if not degree:
        return helpers.api_error("Degree {} not found".format(degree_id), status.HTTP_400_BAD_REQUEST)
    
    tutor_user_id = parsed_body.get('userId', None)
    price = parsed_body.get('price', None)   
    post_text = parsed_body.get('postText')

    courses = parsed_body.get('courses', None)

    if not (tutor_user_id and price and courses):
        return helpers.api_error("Invalid fields: tutorUserId: {}, price: {}, courses: {}".
                            format(tutor_user_id, price, courses), status.HTTP_400_BAD_REQUEST)

    user = storage.get_user_by_id(tutor_user_id)

    if not user:
        return helpers.api_error("Could not find user with id: {}.".format(tutor_user_id), status.HTTP_400_BAD_REQUEST)

    
    if user.user_type == models.UserType.Student.value:
        return helpers.api_error("User with id: {} is a student.".format(tutor_user_id), status.HTTP_400_BAD_REQUEST)
    
    
    existing = storage.get_tutor_posting_for_degree(degree).filter(tutor=user)

    if existing: # Check if if we have already created a tutor profile for this user
        return helpers.api_error("User has an existing posting for degree: {}.".format(degree_id), status.HTTP_400_BAD_REQUEST)

    # try:
    posting, courses = storage.create_tutor_posting(user, degree, price, post_text, courses)
    
    result = serializers.tutor_posting_to_dict(posting)
    result.update({'courses': [serializers.posting_course_to_dict(course) for course in courses]})

    return helpers.api_success({'posting': result})

    # except Exception as ex:
    #     return helpers.api_error("Error occured creating TutorInformation and Courses. Exception: {}".
    #         format(str(ex)), status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    tutor = storage.get_tutor_by_id(tutor_id).first()
    if not tutor:
        return helpers.api_error("Tutor {} not found".format(tutor_id), status.HTTP_400_BAD_REQUEST)

    reviews = storage.get_tutor_reviews(tutor)
    return helpers.api_success({'reviews': [serializers.tutor_review_to_dict(review) for review in reviews]})
    
@helpers.parse_api_json_body
def add_tutor_review(request, tutor_id, parsed_body=None):
    tutor = storage.get_tutor_by_id(tutor_id).first()

    if not tutor:
        return helpers.api_error("Tutor {} not found".format(tutor_id), status.HTTP_400_BAD_REQUEST)

    review_text = parsed_body.get('reviewText', None)
    rating = parsed_body.get('rating', None)   
    user_id = parsed_body.get('userId', None)

    if not (review_text and rating and user_id):
        return helpers.api_error("Invalid fields: review text: {} rating: {} user_id: {}".format(
                            review_text, rating, user_id), status.HTTP_400_BAD_REQUEST)

    user_review_from = storage.get_user_by_id(user_id)

    if not user_review_from:
        return helpers.api_error("Could not find user with id: {}".format(user_id), status.HTTP_400_BAD_REQUEST)

    if user_review_from.id == tutor.id:
        return helpers.api_error("user_id of reviewer must be different from user_id of tutor".
            format(user_id), status.HTTP_400_BAD_REQUEST)

    # Check this user hasnt already left a review for this tutor
    existing_review = storage.get_tutor_reviews(tutor).filter(user=user_review_from)

    if existing_review:
        return helpers.api_error("There already exists review for tutor: {} from user: {}".
            format(tutor.id, user_id), status.HTTP_400_BAD_REQUEST)

    try:
        new_review = storage.create_review_for_tutor(tutor, review_text, rating, user_review_from)
        return helpers.api_success({'review': serializers.tutor_review_to_dict(new_review)})

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
    firebase_id = request.GET.get('firebaseId')

    if not firebase_id:
        return helpers.api_error('pass the firebaseId as a query param', status.HTTP_400_BAD_REQUEST)
    
    user = storage.get_user_from_firebase(firebase_id)

    if not user:
        return helpers.api_error('Could not find a user with firebase_id: {}'.format(firebase_id), status.HTTP_400_BAD_REQUEST)

    result = {'user': serializers.user_to_dict(user)}

    if user.user_type == models.UserType.Tutor.value:
        tutor_postings = storage.get_tutor_postings(user)
        avg_rating, tutor_reviews = storage.get_tutor_ratings_reviews(user)

        result['user'].update({'postings': [serializers.tutor_posting_to_dict(posting) for posting in tutor_postings]})
        result['user'].update({'reviews': [serializers.tutor_review_to_dict(review) for review in tutor_reviews]})
        result['user'].update({'avgRating': avg_rating})

    else:
        result['user'].update({'contactedTutors': None})


    return helpers.api_success(result)


@helpers.parse_api_json_body
def create_user(request, parsed_body=None):
    school_id = parsed_body.get('schoolId', None)
    name = parsed_body.get('name', None)
    user_type = parsed_body.get('userType', 'student') # Defaults to student
    firebase_id = parsed_body.get('firebaseId', None)
    phone_number = parsed_body.get('phoneNumber', None)
    lat = parsed_body.get('lat', None)
    lon = parsed_body.get('lon', None)

    if not (school_id and firebase_id and name and phone_number):
        return helpers.api_error('Invalid fields: schoolId: {}, name: {}, firebaseId: {} phoneNumber: {}'.format(
            school_id, name, firebase_id, phone_number), status.HTTP_400_BAD_REQUEST)

    school = storage.get_school_by_id(school_id)

    if not school:
        return helpers.api_error('School with id: {} not found'.format(school_id), status.HTTP_400_BAD_REQUEST)

    try:
        user_type = models.UserType(user_type).value
        user_info = storage.create_user_info(school, name, phone_number, user_type, firebase_id, lat, lon)

        return helpers.api_success({'user': serializers.user_to_dict(user_info)})

    except Exception as ex:
        return helpers.api_error("Error occured while creating a User. Exception: {}".
            format(str(ex)), status.HTTP_500_INTERNAL_SERVER_ERROR)


