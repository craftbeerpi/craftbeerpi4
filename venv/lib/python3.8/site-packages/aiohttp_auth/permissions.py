from enum import Enum, unique


@unique
class Permission(Enum):
    Allow = True
    Deny = False


@unique
class Group(Enum):
    Everyone = 'aiohttp_auth.acl.group.Everyone'
    AuthenticatedUser = 'aiohttp_auth.acl.group.AuthenticatedUser'

