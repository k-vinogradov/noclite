import traceback

from django.http import HttpRequest


class ExceptionCatacher:
    def __init__(self):
        pass

    def process_exception(self, request, exception):
        """
        :param request: HttpRequest
        :type request: HttpRequest
        :param exception: Exception
    `   :type exception: Exception
        """
        print exception
        traceback.print_exc();
        return None
