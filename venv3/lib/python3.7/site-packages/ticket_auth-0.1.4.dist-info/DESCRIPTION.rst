ticket_auth
===========

Simple library that provides a mod_auth_tkt like hashed tickets that can be
used for storing user authentication details.

The library is not interchangable with the mod_auth_tkt format, as the
mod_auth_tkt does not provide support for ipv6 addresses and different hash
algorithms, whereas ticket_auth provides both.

Usage
-----

The general format for using the library is to instantiate the ticket factory
used to generate the tickets, and then create new tickets or validate existing
tickets using that factory. For example::

    # The ticket factory takes a bytes argument specifying the secret
    # identifier, and a optional algorithm (defaults to sha512). Possible
    # algorithms are those specified by the python hashlib library
    factory = TicketFactory(b'secret', hashalg='md5')

    # The new function returns a new ticket (as a string). It takes a user
    # identifier as a argument, along with several optional arguments. The
    # valid_until argument is the time at which the ticket expires.
    valid_until = time.time() + 60
    ticket = factory.new('test_id', valid_until=valid_until)

    # A ticket can be validated with the validate function. It returns a
    # TicketInfo value on success, or raises an error on failure
    info = factory.validate(ticket)

Tickets can also be bound to a particular client ip address by passing a
ip address like object (either string, or from module ip_address) as the
client_ip argument when creating and validating the string. For example::

    valid_until = time.time() + 60
    ticket = factory.new('test_id', valid_until=valid_until,
                         client_ip='192.168.0.1')

    info = factory.validate(ticket, client_ip='192.168.0.1')

A sequence of tokens can also be passed, which will be added to the ticket.
Note that these tokens (like the user id and user data) are stored in plain
text format::

    ticket = factory.new('test_id', valid_until=valid_until, tokens=('a', 'b'),
                         user_data='some data')

The TicketInfo object returned by the validate function is a named tuple with
the following parameters: digest (hash function output), user_id, tokens,
user_data, valid_until.

License
-------

The library is licensed under a MIT license.


