from . import models
from django.db import transaction
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist



def safe_get(entity_class, **params):
    try:
        return entity_class.objects.get(**params)
    except (entity_class.DoesNotExist, MultipleObjectsReturned):
        # need loggin
        # raise
        return None

def get_degrees(school_id):
    return models.Degree.objects.filter(school=school_id)

def get_tutors(degree):
    return models.TutorInformation.objects.filter(degree=degree)
    
def get_courses_per_tutor(tutor):
    return models.TutoredCourse.objects.filter(tutor_id=tutor)

def get_tutor_ratings_reviews(tutor):
    ratings = models.TutorReview.objects.filter(tutor=tutor)
    total_ratings = len(ratings)
    avg_rating = 0

    if total_ratings != 0:
        avg_rating = sum([review.rating for review in ratings])/len(ratings)

    return avg_rating,ratings

def get_degree_by_id(id):
    return safe_get(models.Degree, id=id)

def create_tutor_information_for_degree(user, degree, hourly_rate, lat, lon, phone_number, courses):
    try:
        with transaction.atomic():
            tutor = create_tutor_info(user, degree, hourly_rate, lat, lon, phone_number)
            courses = create_tutored_courses(tutor, courses)
            return tutor, courses
    except: 
        # logging 
        raise

def get_course_by_id(c_id):
    return safe_get(models.Course, id=c_id)

def create_tutored_courses(tutor, courses):
    for c_id in courses:  
        course = get_course_by_id(c_id)
        if not course:
            raise Exception("Invalid Course Id: {}".format(c_id))
        models.TutoredCourse.objects.create(tutor=tutor, course=course)
        
    return get_courses_per_tutor(tutor)

def get_user_from_firebase(firebase_id):
    return safe_get(models.UserInformation, firebase_id=firebase_id)

def get_tutor_information_for_user(user):
    return safe_get(models.TutorInformation, user=user)

def create_tutor_info(user, degree, hourly_rate, lat, lon, phone_number):
    return models.TutorInformation.objects.create(
        user=user,
        degree=degree,
        hourly_rate=hourly_rate,
        lat=lat,
        lon=lon,
        phone_number=phone_number)

def get_courses_by_degree(degree):
    return models.Course.objects.filter(degree=degree)

def get_schools():
    return models.School.objects.all()

def get_tutor_by_id(id):
    return safe_get(models.TutorInformation, id=id)

def get_tutor_reviews(tutor):
    return models.TutorReview.objects.filter(tutor=tutor)

def get_user_by_id(id):
    return safe_get(models.UserInformation, id=id)

def create_review_for_tutor(tutor, comment, rating, user):
    return models.TutorReview.objects.create(
        tutor=tutor,
        comment=comment,
        rating=rating,
        user=user
    )

def get_school_by_id(school_id):
    return safe_get(models.School, id=school_id)

def create_user_info(school, user_type, firebase_id):
    return models.UserInformation.objects.create(
        user_type=user_type,
        school=school,
        firebase_id=firebase_id)