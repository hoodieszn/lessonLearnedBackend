from django.contrib import admin
# Register your models here.

from core.models import (
    Degree,
    School
)

models = [School, Degree]

class DegreeAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name', 'school']


class SchoolAdmin(admin.ModelAdmin):
    list_display = ['pk', 'name']



for model in models:
    if '{}Admin'.format(model.__name__) in globals():
        admin.site.register(model, globals()['{}Admin'.format(model.__name__)])
    else:
        admin.site.register(model)
