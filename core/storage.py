from . import models

def get_degrees(school_id):
    return models.Degree.objects.filter(school=school_id)


