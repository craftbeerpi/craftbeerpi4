from .ticket_auth import TktAuthentication


COOKIE_AUTH_KEY = 'aiohttp_auth.auth.CookieTktAuthentication'


class CookieTktAuthentication(TktAuthentication):
    """Ticket authentication mechanism based on the ticket_auth library, with
    ticket data being stored as a cookie in the response.
    """

    async def remember_ticket(self, request, ticket):
        """Called to store the ticket data for a request.

        Ticket data is stored in COOKIE_AUTH_KEY in the request object, and
        written as cookie data to the response during the process_response()
        function.

        Args:
            request: aiohttp Request object.
            ticket: String like object representing the ticket to be stored.
        """
        request[COOKIE_AUTH_KEY] = ticket

    async def forget_ticket(self, request):
        """Called to forget the ticket data a request

        Args:
            request: aiohttp Request object.
        """
        request[COOKIE_AUTH_KEY] = ''

    async def get_ticket(self, request):
        """Called to return the ticket for a request.

        Args:
            request: aiohttp Request object.

        Returns:
            A ticket (string like) object, or None if no ticket is available
            for the passed request.
        """
        return request.cookies.get(self.cookie_name, None)

    async def process_response(self, request, response):
        """Called to perform any processing of the response required.

        This function stores any cookie data in the COOKIE_AUTH_KEY as a
        cookie in the response object. If the value is a empty string, the
        associated cookie is deleted instead.

        This function requires the response to be a aiohttp Response object,
        and assumes that the response has not started if the remember or
        forget functions are called during the request.

        Args:
            request: aiohttp Request object.
            response: response object returned from the handled view

        Raises:
            RuntimeError: Raised if response has already started.
        """
        await super().process_response(request, response)
        if COOKIE_AUTH_KEY in request:
            if response.started:
                raise RuntimeError("Cannot save cookie into started response")

            cookie = request[COOKIE_AUTH_KEY]
            if cookie == '':
                response.del_cookie(self.cookie_name)
            else:
                response.set_cookie(self.cookie_name, cookie)
