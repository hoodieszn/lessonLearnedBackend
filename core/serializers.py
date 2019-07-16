from . import models
from . import storage

def degree_to_dict(degree):
    return {'id': degree.id, 
            'name': degree.name,
            'schoolId': degree.school.id,
            'schoolName': degree.school.name}

def tutor_posting_to_dict(tutor_posting):
    return {'id': tutor_posting.id,
            'tutorName': tutor_posting.tutor.name,
            'phoneNumber': tutor_posting.tutor.phone_number,
            'lat': tutor_posting.tutor.lat,
            'lon': tutor_posting.tutor.lon,
            'tutorId': tutor_posting.tutor.id,
            'degree': tutor_posting.degree.name,
            'price': tutor_posting.price,
            'postText': tutor_posting.post_text}

def posting_course_to_dict(posting_course):
    return {'courseId': posting_course.course.id,
            'postingId': posting_course.tutor_posting.id}

def course_to_dict(course):
    return {'id': course.id,
            'name': course.name}

def tutor_review_to_dict(tutor_review):
    return {'tutorName': tutor_review.tutor.name,
            'reviewText': tutor_review.review_text,
            'rating': tutor_review.rating,
            'userId': tutor_review.user.id, 
            'tutorId': tutor_review.tutor.id,
            'date': tutor_review.created_at}

def school_to_dict(school):
    return {'id': school.id,
            'name': school.name}


def user_to_dict(user):
    user_type = user.user_type
    if type(user.user_type) is not str:
        user_type = user_type.value

    return {'id': user.id,
            'userType': user_type,
            'schoolId': user.school.id,
            'firebaseId': user.firebase_id,
            'phoneNumber': user.phone_number,
            'lat': user.lat, 
            'lon': user.lon,
            'name': user.name}

def tutor_contact_to_dict(tutor_contact):
    return {'id': tutor_contact.id, 
            'userId': tutor_contact.user.id,
            'tutorInfo': user_to_dict(tutor_contact.tutor)}