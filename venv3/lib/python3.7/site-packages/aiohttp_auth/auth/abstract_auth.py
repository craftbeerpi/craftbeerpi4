import abc

class AbstractAuthentication(object):
    """Abstract authentication policy class"""

    @abc.abstractmethod
    async def remember(self, request, user_id):
        """Abstract function called to store the user_id for a request.

        Args:
            request: aiohttp Request object.
            user_id: String representing the user_id to remember
        """
        pass

    @abc.abstractmethod
    async def forget(self, request):
        """Abstract function called to forget the userid for a request

        Args:
            request: aiohttp Request object
        """

        pass

    @abc.abstractmethod
    async def get(self, request):
        """Abstract function called to get the user_id for the request.

        Args:
            request: aiohttp Request object.

        Returns:
            The user_id for the request, or None if the user_id is not
            authenticated.
        """
        pass

    async def process_response(self, request, response):
        """Called to perform any processing of the response required (setting
        cookie data, etc).

        Default implementation does nothing.

        Args:
            request: aiohttp Request object.
            response: response object returned from the handled view
        """
        pass