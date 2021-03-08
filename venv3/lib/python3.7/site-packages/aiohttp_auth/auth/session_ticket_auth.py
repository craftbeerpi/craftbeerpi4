from aiohttp_session import get_session
from .ticket_auth import TktAuthentication


class SessionTktAuthentication(TktAuthentication):
    """Ticket authentication mechanism based on the ticket_auth library, with
    ticket data being stored in the aiohttp_session object.
    """

    async def remember_ticket(self, request, ticket):
        """Called to store the ticket data for a request.

        Ticket data is stored in the aiohttp_session object

        Args:
            request: aiohttp Request object.
            ticket: String like object representing the ticket to be stored.
        """
        session = await get_session(request)
        session[self.cookie_name] = ticket

    async def forget_ticket(self, request):
        """Called to forget the ticket data a request

        Args:
            request: aiohttp Request object.
        """
        session = await get_session(request)
        session.pop(self.cookie_name, '')

    async def get_ticket(self, request):
        """Called to return the ticket for a request.

        Args:
            request: aiohttp Request object.

        Returns:
            A ticket (string like) object, or None if no ticket is available
            for the passed request.
        """
        session = await get_session(request)
        return session.get(self.cookie_name)
