from django.contrib import admin
# Register your models here.

from core.models import (
    Course,
    Degree,
    School,
    TutoredCourse,
    TutorReview,
    TutorInformation,
    UserInformation
)

models = [Course, School, Degree, TutoredCourse, TutorReview, TutorInformation, UserInformation]

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

class TutoredCourseAdmin(admin.ModelAdmin):
    list_display = ['pk', 'course', 'tutor']

class TutorInformationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'phone_number', 'lat', 'lon']

    # def degree_name(self, obj):
    #     return obj.degree.name

class TutorReviewAdmin(admin.ModelAdmin):
    list_display = ['pk', 'comment', 'rating', 'user']


class UserInformationAdmin(admin.ModelAdmin):
    list_display = ['pk', 'school', 'firebase_id']


for model in models:
    if '{}Admin'.format(model.__name__) in globals():
        admin.site.register(model, globals()['{}Admin'.format(model.__name__)])
    else:
        admin.site.register(model)
