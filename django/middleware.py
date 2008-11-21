from django.http import Http404
from wrapper import post

class AreciboMiddleware(object):
    def process_exception(self, request, exception):
        """ This is middleware to process a request 
        and pass the value off to Arecibo. """
        if isinstance(exception, Http404):
            post(request, 404)
        else:
            # do we want to do further look up
            # more information
            post(request, 500)