from . import storage
from . import serializers
from . import helpers
from rest_framework import status
from django.views.decorators.http import require_GET, require_POST, require_http_methods

# need to implement token auth or something

@require_GET
def get_degrees(request, school_id):
    # Return All the degrees for a given school should we use Waterloo API
    degrees = storage.get_degrees(school_id)
    return helpers.api_success({'degrees': [serializers.degree_to_dict(deg) for deg in degrees]})