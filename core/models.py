from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from enum import Enum

def is_django_model(x):
    return isinstance(x, models.Model)

class UserType(Enum):   # making this an enum instead we want to extend
    Student = 'student'
    Tutor = 'tutor'

class School(models.Model):
    name = models.CharField(max_length=150)
    created_at = models.DateTimeField(auto_now_add=True)

class UserInformation(models.Model):
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=30, null=False, blank=False)
    user_type = models.CharField(max_length=10, choices=[(str(tag.value), tag.value) for tag in UserType])
    phone_number = models.CharField(max_length=10, null=False, blank=False)
    firebase_id = models.CharField(max_length=128, default='', unique=True)
    lat = models.FloatField(blank=True, null=True) # not yet sure what the best way to store location is
    lon = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Degree(models.Model):
    name = models.CharField(max_length=150)
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Course(models.Model):
    name = models.CharField(max_length=100)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class TutorPosting(models.Model):
    tutor = models.ForeignKey(UserInformation, on_delete=models.CASCADE)
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    post_text = models.CharField(max_length=300, null=False, blank=False)

class PostingCourse(models.Model):
    tutor_posting = models.ForeignKey(TutorPosting, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete = models.CASCADE)

class TutorReview(models.Model):
    review_text = models.CharField(max_length=400, blank=True)
    rating = models.IntegerField(default=1, validators=[MaxValueValidator(5), MinValueValidator(1)])
    tutor = models.ForeignKey(UserInformation, null=True, on_delete=models.SET_NULL, related_name='%(class)s_review_for')
    user = models.ForeignKey(UserInformation, null=True, on_delete=models.SET_NULL, related_name='%(class)s_review_created')
    created_at = models.DateTimeField(auto_now_add=True)

class TutorContacts(models.Model):
    tutor = models.ForeignKey(UserInformation, null=True, on_delete=models.SET_NULL, related_name='%(class)s_contactee')
    user = models.ForeignKey(UserInformation, null=True, on_delete=models.SET_NULL, related_name='%(class)s_contacted')

class AbuseReport(models.Model):
    tutor = models.ForeignKey(UserInformation, null=True, on_delete=models.SET_NULL, related_name='%(class)s_reported')
    user = models.ForeignKey(UserInformation, null=True, on_delete=models.SET_NULL, related_name='%(class)s_reportee')
    report_reason = models.CharField(max_length=400, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
