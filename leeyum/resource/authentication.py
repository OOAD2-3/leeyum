from rest_framework.authentication import SessionAuthentication


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        """
        To not perform the csrf check previously happening
        """
        return
