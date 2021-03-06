from . import storage
from . import serializers
from . import helpers
from . import models
from rest_framework import status
from django.views.decorators.http import require_GET, require_POST, require_http_methods
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_swagger import renderers
from rest_framework.decorators import api_view, renderer_classes, permission_classes
from rest_framework import response, schemas


# need to implement token auth or something


@api_view()
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([AllowAny])
def schema_view(request):
    generator = schemas.SchemaGenerator(title='API')
    return response.Response(generator.get_schema(request=request))


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
@require_GET
def get_degrees(request, school_id):
    # Return All the degrees for a given school
    degrees = storage.get_degrees(school_id)
    return helpers.api_success({'degrees': [serializers.degree_to_dict(deg) for deg in degrees]})


@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
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
            'avgRating': avg_rating,
        })
    
    return helpers.api_success({'tutorPostings': result})

@helpers.parse_api_json_body
@require_http_methods(["POST"])
@permission_classes([IsAuthenticated])
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

    try:
        posting, courses = storage.create_tutor_posting(user, degree, price, post_text, courses)
        
        result = serializers.tutor_posting_to_dict(posting)
        result.update({'courses': [serializers.posting_course_to_dict(course) for course in courses]})

        return helpers.api_success({'posting': result})

    except Exception as ex:
        return helpers.api_error("Error occured creating TutorInformation and Courses. Exception: {}".
            format(str(ex)), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
def get_courses(request, degree_id):

    degree = storage.get_degree_by_id(degree_id)

    if not degree:
        return helpers.api_error("Degree {} not found".format(degree_id), status.HTTP_400_BAD_REQUEST)

    course_subject = request.GET.get('subject')

    courses_for_degree = storage.get_courses_by_degree(degree)

    if course_subject:
        courses_for_degree = courses_for_degree.filter(name__contains=course_subject)

    return helpers.api_success({'courses': [serializers.course_to_dict(course) for course in courses_for_degree]})

@api_view(['GET'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
def get_schools(request):

    schools = storage.get_schools()
    return helpers.api_success({'schools': [serializers.school_to_dict(school) for school in schools]})

@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
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

    result = get_user_data(user)

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

        result = {'user': serializers.user_to_dict(user_info)}

        if user_type == 'tutor':
            result['user'].update({'avgRating': 0})
            result['user'].update({'reviews': []})
            result['user'].update({'postings': []})

        return helpers.api_success(result)

    except Exception as ex:
        return helpers.api_error("Error occured while creating a User. Exception: {}".
            format(str(ex)), status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
def handle_tutor_contacts(request):
    if request.method == 'GET':
        return get_tutor_contacts(request)
    elif request.method == 'POST':
        return create_tutor_contact(request)


def get_tutor_contacts(request):
    user_id = request.GET.get('userId')

    if not user_id:
        return helpers.api_error('Include a userId as a query param', status.HTTP_400_BAD_REQUEST)

    user = storage.get_user_by_id(user_id)

    if not user:
        return helpers.api_error('User with id: {} not found'.format(user_id), status.HTTP_400_BAD_REQUEST)

    contacts = storage.get_contacted_tutors_for_user(user)
    contacted_tuts = []

    for contact in contacts:
        contact_reported = storage.check_if_reported(contact.user, contact.tutor)

        serialize_contact = serializers.tutor_contact_to_dict(contact)
        serialize_contact.update({'reported': contact_reported})

        contacted_tuts.append(serialize_contact)
    
    return helpers.api_success({'contacts': contacted_tuts})


@helpers.parse_api_json_body
def create_tutor_contact(request, parsed_body=None):
    tutor_id = parsed_body.get('tutorId', None)
    user_id = parsed_body.get('userId', None)

    if not (tutor_id and user_id):
        return helpers.api_error('Invalid fields. userId: {} tutorId: {}'.format(user_id, tutor_id), status.HTTP_400_BAD_REQUEST)

    
    user = storage.get_user_by_id(user_id)
    tutor = storage.get_user_by_id(tutor_id)

    if not user:
        return helpers.api_error('User with id: {} not found'.format(user_id), status.HTTP_400_BAD_REQUEST)

    if not tutor:
        return helpers.api_error('Tutor with id: {} not found'.format(tutor_id), status.HTTP_400_BAD_REQUEST)


    existing_contact = storage.get_contacted_tutors_for_user(user).filter(tutor=tutor)

    if existing_contact: 
        return helpers.api_error('Already exists a TutorContact for User: {} and Tutor: {}.'.format(user_id, tutor_id), status.HTTP_400_BAD_REQUEST)

    contact = storage.create_tutor_contact(user, tutor)

    return helpers.api_success({'contact': serializers.tutor_contact_to_dict(contact)})


@api_view(['GET', 'PUT'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
@helpers.parse_api_json_body
def handle_user_by_id(request, user_id, parsed_body=None):
    if request.method == 'GET':
        return get_user_by_id(request, user_id)
    elif request.method == 'PUT':
        return update_user(request, user_id, parsed_body)



def get_user_by_id(request, user_id):
    user = storage.get_user_by_id(user_id)

    if not user:
        return helpers.api_error('User: {} does not exist.'.format(user_id), status.HTTP_400_BAD_REQUEST)

    result = get_user_data(user)

    return helpers.api_success(result)


def update_user(request, user_id, parsed_body):
    lat = parsed_body.get('lat', None)
    lon = parsed_body.get('lon', None)

    if not (lat and lon):
        return helpers.api_error('Invalid Fields. lat: {}, lon: {}'.format(lat, lon))

    user = storage.get_user_by_id(user_id)

    if not user:
        return helpers.api_error('Could not find user with id: {}'.format(user_id))

    updated_user = storage.update_user(user, lat, lon)

    return helpers.api_success({'user': serializers.user_to_dict(updated_user)})
    

@api_view(['POST'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
@helpers.parse_api_json_body
def create_abuse_report(request, parsed_body=None):
    tutor_id = parsed_body.get('tutorId', None)
    user_id = parsed_body.get('userId', None)
    report_msg = parsed_body.get('reportReason', None)

    if not (tutor_id and user_id and report_msg):
            return helpers.api_error('Invalid fields. userId: {} tutorId: {} reportReason'.format(
                user_id, tutor_id, report_msg), status.HTTP_400_BAD_REQUEST)


    tutor = storage.get_user_by_id(tutor_id)

    if not tutor:
        return helpers.api_error('Tutor with id: {} not found'.format(tutor_id), status.HTTP_400_BAD_REQUEST)

    user = storage.get_user_by_id(user_id)

    if not user:
        return helpers.api_error('User with id: {} not found'.format(user_id), status.HTTP_400_BAD_REQUEST)

    try:
        abuse_report = storage.create_abuse_report(user, tutor, report_msg)

        return helpers.api_success({'abuseReport': serializers.abuse_report_to_dict(abuse_report)})

    except Exception as ex:
        return helpers.api_error("Error creating AbuseReport. Ex: {}".
            format(str(ex)), status.HTTP_500_INTERNAL_SERVER_ERROR)



def get_user_data(user):
    result = {'user': serializers.user_to_dict(user)}

    if user.user_type == models.UserType.Tutor.value:
        tutor_postings = storage.get_tutor_postings(user)
        avg_rating, tutor_reviews = storage.get_tutor_ratings_reviews(user)

        serialized_tutor_postings = []

        for posting in tutor_postings:
            serialized_posting = serializers.tutor_posting_to_dict(posting) 
            tutored_courses = storage.get_courses_per_posting(posting)

            serialized_posting.update({
                'courses': [serializers.course_to_dict(course.course) for course in tutored_courses],
            })

            serialized_tutor_postings.append(serialized_posting)

        result['user'].update({'postings': serialized_tutor_postings})
        result['user'].update({'reviews': [serializers.tutor_review_to_dict(review) for review in tutor_reviews]})
        result['user'].update({'avgRating': avg_rating})

    else:
        contacts = storage.get_contacted_tutors_for_user(user)

        contacted_tuts = []
        for contact in contacts:
            contact_reported = storage.check_if_reported(contact.user, contact.tutor)

            serialize_contact = serializers.tutor_contact_to_dict(contact)
            serialize_contact.update({'reported': contact_reported})
            
            contacted_tuts.append(serialize_contact)
        
        result['user'].update({'contactedTutors': contacted_tuts})

    return result

@api_view(['DELETE'])
@renderer_classes([renderers.OpenAPIRenderer, renderers.SwaggerUIRenderer])
@permission_classes([IsAuthenticated])
def delete_posting(request, posting_id):
    posting = storage.get_posting_by_id(posting_id)

    if not posting:
        return helpers.api_error('Posting with id: {} not found'.format(posting_id), status.HTTP_400_BAD_REQUEST)

    posting.delete()

    return helpers.api_success('Posting with id: {} deleted'.format(posting_id))