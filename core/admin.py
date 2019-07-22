from django.contrib import admin
# Register your models here.

from core.models import (
    Course,
    Degree,
    School,
    PostingCourse,
    TutorReview,
    TutorPosting,
    UserInformation,
    AbuseReport,

)

models = [Course, School, Degree, PostingCourse, TutorReview, TutorPosting, UserInformation, AbuseReport]

class AbuseReportAdmin(admin.ModelAdmin):
    list_display = ['pk', 'tutor_name', 'user_name', 'report_reason']

    def tutor_name(self, obj):
        return obj.tutor.name

    def user_name(self, obj):
        return obj.user.name

class CourseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'degree_name', 'school_name']

    def degree_name(self, obj):
        return obj.degree.name

    def school_name(self, obj):
        return obj.degree.school.name

class DegreeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'school',]

class SchoolAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']

class PostingCourseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'course', 'tutor_posting']

    # def degree_name(self, obj):
    #     return obj.degree.name

class TutorReviewAdmin(admin.ModelAdmin):
    list_display = ['pk', 'review_text', 'rating', 'user']


class UserInformationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'school', 'name', 'firebase_id']


for model in models:
    if '{}Admin'.format(model.__name__) in globals():
        admin.site.register(model, globals()['{}Admin'.format(model.__name__)])
    else:
        admin.site.register(model)
