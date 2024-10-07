import json
from rest_framework.views import exception_handler
from rest_framework import serializers

from rest_framework.exceptions import ParseError
from django.http import JsonResponse
from django.http import Http404


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if isinstance(exc, serializers.ValidationError):
        response.data = {
            'status': 'error',
            'message': "Validation Error",
            'errors': response.data,
        }

    # Handle JSON Parse Errors (ParseError or JSONDecodeError)
    if isinstance(exc, ParseError) or isinstance(exc, json.JSONDecodeError):
        return JsonResponse({
            'status': 'error',
            'message': "Invalid JSON data provided",
            'errors': str(exc)
        }, status=400)

    # Handle NotFound (No Account matches the given query)
    if isinstance(exc, Http404):
        return JsonResponse({
            'status': 'error',
            'message': "Account not found",
            'errors': str(exc)
        }, status=404)

    return response
