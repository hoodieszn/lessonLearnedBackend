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

def get_tutor_posting_for_degree(degree):
    return models.TutorPosting.objects.filter(degree=degree)
    
def get_courses_per_posting(posting):
    return models.PostingCourse.objects.filter(tutor_posting=posting)

def get_tutor_ratings_reviews(tutor):
    ratings = models.TutorReview.objects.filter(tutor=tutor)
    total_ratings = len(ratings)
    avg_rating = 0

    if total_ratings != 0:
        avg_rating = sum([review.rating for review in ratings])/len(ratings)

    return avg_rating,ratings

def get_degree_by_id(id):
    return safe_get(models.Degree, id=id)


def create_tutor_posting(tutor, degree, price, post_text, courses):
    try:
        with transaction.atomic():
            posting = create_posting(tutor, degree, price, post_text)
            courses = create_courses_for_posting(posting, courses)
            return posting, courses
    except: 
        # logging 
        raise

def get_course_by_id(c_id):
    return safe_get(models.Course, id=c_id)

def create_posting(tutor, degree, price, post_text):
    return models.TutorPosting.objects.create(
        tutor=tutor,
        degree=degree,
        price=price,
        post_text=post_text)

def create_courses_for_posting(posting, courses):
    for c_id in courses:  
        course = get_course_by_id(c_id)
        if not course:
            raise Exception("Invalid Course Id: {}".format(c_id))
        models.PostingCourse.objects.create(tutor_posting=posting, course=course)
        
    return get_courses_in_posting(posting)

def get_courses_in_posting(posting):
    return models.PostingCourse.objects.filter(tutor_posting=posting)

def get_user_from_firebase(firebase_id):
    return safe_get(models.UserInformation, firebase_id=firebase_id)

def get_tutor_information_for_user(user):
    return safe_get(models.TutorInformation, user=user)


def get_courses_by_degree(degree):
    return models.Course.objects.filter(degree=degree)

def get_schools():
    return models.School.objects.all()

def get_tutor_by_id(id):
    return models.UserInformation.objects.filter(id=id, user_type='tutor')
    # return safe_get(models.UserInformation, id=id).filter(user_type=tutor)

def get_tutor_reviews(tutor):
    return models.TutorReview.objects.filter(tutor=tutor)

def get_tutor_postings(tutor):
    return models.TutorPosting.objects.filter(tutor=tutor)

def get_user_by_id(id):
    return safe_get(models.UserInformation, id=id)

def create_review_for_tutor(tutor, review_text, rating, user):
    return models.TutorReview.objects.create(
        tutor=tutor,
        review_text=review_text,
        rating=rating,
        user=user
    )

def get_school_by_id(school_id):
    return safe_get(models.School, id=school_id)

def create_user_info(school, name, phone_number, user_type, firebase_id, lat, lon):
    return models.UserInformation.objects.create(
        user_type=user_type,
        name=name,
        phone_number=phone_number,
        lat=lat,
        lon=lon,
        school=school,
        firebase_id=firebase_id)

def get_contacted_tutors_for_user(user):
    return models.TutorContacts.objects.filter(user=user)

def create_tutor_contact(user, tutor):
    return models.TutorContacts.objects.create(user=user, tutor=tutor)

def get_reported_users(user):
    return models.AbuseReport.objects.filter(user=user)

def check_if_reported(user, tutor):
    return get_reported_users(user).filter(tutor=tutor).count() > 0