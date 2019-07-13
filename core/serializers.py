from . import models
from . import storage

def degree_to_dict(degree):
    return {'id': degree.id, 
            'name': degree.name,
            'school': degree.school.id}


def tutor_to_dict(tutor):
    return {'id': tutor.id,
            'degree': tutor.degree.name,
            'hourly_rate': tutor.hourly_rate,
            'lat': tutor.lat, 
            'lon': tutor.lon}


def course_to_dict(course):
    return {'id': course.id,
            'name': course.name}


def tutor_review_to_dict(tutor_review):
    return {'comment': tutor_review.comment,
            'rating': tutor_review.rating,
            'user_id': tutor_review.user.id, 
            'tutor_id': tutor_review.tutor.id}


def school_to_dict(school):
    return {'id': school.id,
            'name': school.name}

def review_to_dict(review):
    return {'id': review.id,
            'comment': review.comment,
            'rating': review.rating,
            'tutor_id': review.tutor.id,
            'tutor_user_id': review.tutor.user.id,
            'user_id': review.user.id}