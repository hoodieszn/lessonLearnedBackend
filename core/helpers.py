from rest_framework import status
from django.http import JsonResponse

from core import models, serializers

MODEL_SERIALIZERS = {
       models.Degree.__name__: serializers.degree_to_dict
}

def serialize_django_model(model_instance):
    class_key = model_instance.__class__.__name__
    serialize = MODEL_SERIALIZERS.get(class_key)
    if not serialize:
        raise NotImplementedError('No serializer registered for {}'.format(class_key))
    return serialize(model_instance)


def api_success(data, status_code=status.HTTP_200_OK):
    dict_data = serialize_django_model(data) if models.is_django_model(data) else data
    return JsonResponse({'data': dict_data}, status=status_code)


def api_error(message, status_code=status.HTTP_200_OK):
    return JsonResponse({'error': message}, status=status_code)