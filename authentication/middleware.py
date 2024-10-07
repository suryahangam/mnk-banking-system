import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

# Initialize logger
logger = logging.getLogger(__name__)


class GlobalExceptionMiddleware(MiddlewareMixin):
    '''
    Middleware to handle global exceptions in the application.

    This middleware catches any unhandled exceptions that occur during
    the processing of a request and logs the error. It returns a generic
    JSON response indicating an error has occurred.

    Methods:
        process_exception(request, exception): Logs the exception and 
        returns a JSON response with a 500 status code.
    '''

    def process_exception(self, request, exception):
        logger.error(f'An error occurred: {exception}', exc_info=True)
        return JsonResponse(
            {'status': 'error',
                'message': 'An unexpected error occurred. Please try again later.',
                'error': None
             },
            status=500
        )
