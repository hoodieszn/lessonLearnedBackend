from . import models

def get_degrees(school_id):
    return models.Degree.objects.filter(school=school_id)


def get_tutors(degree):
    return models.TutorInformation.objects.filter(degree=degree)
    
def get_courses_per_tutor(tutor):
    return models.TutoredCourse.objects.filter(tutor_id=tutor)

def get_tutor_reviews(tutor):
    ratings = models.TutorReview.objects.filter(tutor=tutor)
    total_ratings = len(ratings)
    avg_rating = 0

    if total_ratings != 0:
        avg_rating = sum([review.rating for review in ratings])/len(ratings)

    return avg_rating,ratings
