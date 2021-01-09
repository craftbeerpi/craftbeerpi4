from .abstract_auth import AbstractAuthentication

"""Key used to store the auth policy in the request object"""
POLICY_KEY = 'aiohttp_auth.policy'

"""Key used to cache the auth credentials in the request object"""
AUTH_KEY = 'aiohttp_auth.auth'


def auth_middleware(policy):
    """Returns a aiohttp_auth middleware factory for use by the aiohttp
    application object.

    Args:
        policy: A authentication policy with a base class of
            AbstractAuthentication.
    """
    assert isinstance(policy, AbstractAuthentication)

    async def _auth_middleware_factory(app, handler):

        async def _middleware_handler(request):
            # Save the policy in the request
            request[POLICY_KEY] = policy

            # Call the next handler in the chain
            response = await handler(request)

            # Give the policy a chance to handle the response
            await policy.process_response(request, response)

            return response

        return _middleware_handler

    return _auth_middleware_factory


async def get_auth(request):
    """Returns the user_id associated with a particular request.

    Args:
        request: aiohttp Request object.

    Returns:
        The user_id associated with the request, or None if no user is
        associated with the request.

    Raises:
        RuntimeError: Middleware is not installed
    """

    auth_val = request.get(AUTH_KEY)
    if auth_val:
        return auth_val

    auth_policy = request.get(POLICY_KEY)
    if auth_policy is None:
        raise RuntimeError('auth_middleware not installed')

    request[AUTH_KEY] = await auth_policy.get(request)
    return request[AUTH_KEY]


async def remember(request, user_id):
    """Called to store and remember the userid for a request

    Args:
        request: aiohttp Request object.
        user_id: String representing the user_id to remember

    Raises:
        RuntimeError: Middleware is not installed
    """
    auth_policy = request.get(POLICY_KEY)
    if auth_policy is None:
        raise RuntimeError('auth_middleware not installed')

    return await auth_policy.remember(request, user_id)


async def forget(request):
    """Called to forget the userid for a request

    Args:
        request: aiohttp Request object

    Raises:
        RuntimeError: Middleware is not installed
    """
    auth_policy = request.get(POLICY_KEY)
    if auth_policy is None:
        raise RuntimeError('auth_middleware not installed')

    return await auth_policy.forget(request)

