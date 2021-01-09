import abc
import time
from ipaddress import ip_address
from ticket_auth import TicketFactory, TicketError
from .abstract_auth import AbstractAuthentication
from aiohttp import web


_REISSUE_KEY = 'aiohttp_auth.auth.TktAuthentication.reissue'


class TktAuthentication(AbstractAuthentication):
    """Ticket authentication mechanism based on the ticket_auth library.

    This class is an abstract class that creates a ticket and validates it.
    Storage of the ticket data itself is abstracted to allow different
    implementations to store the cookie differently (encrypted, server side
    etc).
    """

    def __init__(
            self,
            secret,
            max_age,
            reissue_time=None,
            include_ip=False,
            cookie_name='AUTH_TKT'):
        """Initializes the ticket authentication mechanism.

        Args:
            secret: Byte sequence used to initialize the ticket factory.
            max_age: Integer representing the number of seconds to allow the
                ticket to remain valid for after being issued.
            reissue_time: Integer representing the number of seconds before
                a valid login will cause a ticket to be reissued. If this
                value is 0, a new ticket will be reissued on every request
                which requires authentication. If this value is None, no
                tickets will be reissued, and the max_age will always expire
                the ticket.
            include_ip: If true, requires the clients ip details when
                calculating the ticket hash
            cookie_name: Name to use to reference the ticket details.
        """
        self._ticket = TicketFactory(secret)
        self._max_age = max_age
        if (self._max_age is not None and
            reissue_time is not None and
            reissue_time < self._max_age):
            self._reissue_time = max_age - reissue_time
        else:
            self._reissue_time = None

        self._include_ip = include_ip
        self._cookie_name = cookie_name

    @property
    def cookie_name(self):
        """Returns the name of the cookie stored in the session"""
        return self._cookie_name

    async def remember(self, request, user_id):
        """Called to store the userid for a request.

        This function creates a ticket from the request and user_id, and calls
        the abstract function remember_ticket() to store the ticket.

        Args:
            request: aiohttp Request object.
            user_id: String representing the user_id to remember
        """
        ticket = self._new_ticket(request, user_id)
        await self.remember_ticket(request, ticket)

    async def forget(self, request):
        """Called to forget the userid for a request

        This function calls the forget_ticket() function to forget the ticket
        associated with this request.

        Args:
            request: aiohttp Request object
        """
        await self.forget_ticket(request)

    async def get(self, request):
        """Gets the user_id for the request.

        Gets the ticket for the request using the get_ticket() function, and
        authenticates the ticket.

        Args:
            request: aiohttp Request object.

        Returns:
            The userid for the request, or None if the ticket is not
            authenticated.
        """
        ticket = await self.get_ticket(request)
        if ticket is None:
            return None

        try:
            # Returns a tuple of (user_id, token, userdata, validuntil)
            now = time.time()
            fields = self._ticket.validate(ticket, self._get_ip(request), now)

            # Check if we need to reissue a ticket
            if (self._reissue_time is not None and
                now >= (fields.valid_until - self._reissue_time)):

                # Reissue our ticket, and save it in our request.
                request[_REISSUE_KEY] = self._new_ticket(request, fields.user_id)

            return fields.user_id

        except TicketError as e:
            return None

    async def process_response(self, request, response):
        """If a reissue was requested, only reiisue if the response was a
        valid 2xx response
        """
        if _REISSUE_KEY in request:
            if (response.started or
                not isinstance(response, web.Response) or
                response.status < 200 or response.status > 299):
                return

            await self.remember_ticket(request, request[_REISSUE_KEY])

    @abc.abstractmethod
    async def remember_ticket(self, request, ticket):
        """Abstract function called to store the ticket data for a request.

        Args:
            request: aiohttp Request object.
            ticket: String like object representing the ticket to be stored.
        """
        pass

    @abc.abstractmethod
    async def forget_ticket(self, request):
        """Abstract function called to forget the ticket data for a request.

        Args:
            request: aiohttp Request object.
        """
        pass

    @abc.abstractmethod
    async def get_ticket(self, request):
        """Abstract function called to return the ticket for a request.

        Args:
            request: aiohttp Request object.

        Returns:
            A ticket (string like) object, or None if no ticket is available
            for the passed request.
        """
        pass

    def _get_ip(self, request):
        ip = None
        if self._include_ip:
            peername = request.transport.get_extra_info('peername')
            if peername:
                ip = ip_address(peername[0])

        return ip

    def _new_ticket(self, request, user_id):
        ip = self._get_ip(request)
        valid_until = int(time.time()) + self._max_age
        return self._ticket.new(user_id, valid_until=valid_until, client_ip=ip)
