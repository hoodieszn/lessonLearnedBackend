from . import models
from . import storage

def degree_to_dict(degree):
    return {'id': degree.id, 
            'name': degree.name,
            'school': degree.school.id}
