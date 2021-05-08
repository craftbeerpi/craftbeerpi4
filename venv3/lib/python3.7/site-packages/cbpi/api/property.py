__all__ = ["PropertyType", "Property"]


class PropertyType(object):
    pass


class Property(object):
    class Select(PropertyType):

        """
        Select Property. The user can select value from list set as options parameter
        """

        def __init__(self, label, options, description=""):
            """

            :param label:
            :param options:
            :param description:
            """
            PropertyType.__init__(self)
            self.label = label
            self.options = options
            self.description = description

    class Number(PropertyType):

        """
        The user can set a number value
        """

        def __init__(
            self, label, configurable=False, default_value=None, unit="", description=""
        ):
            """

            :param label:
            :param configurable:
            :param default_value:
            :param unit:
            :param description:
            """
            PropertyType.__init__(self)
            self.label = label
            self.configurable = configurable
            self.default_value = default_value
            self.description = description

    class Text(PropertyType):

        """
        The user can set a text value
        """

        def __init__(self, label, configurable=False, default_value="", description=""):
            """

            :param label:
            :param configurable:
            :param default_value:
            :param description:
            """
            PropertyType.__init__(self)
            self.label = label
            self.configurable = configurable
            self.default_value = default_value
            self.description = description

    class Actor(PropertyType):

        """
        The user select an actor which is available in the system. The value of this variable will be the actor id
        """

        def __init__(self, label, description=""):
            """

            :param label:
            :param description:
            """
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description

    class Sensor(PropertyType):
        """
        The user select a sensor which is available in the system. The value of this variable will be the sensor id
        """

        def __init__(self, label, description=""):
            """

            :param label:
            :param description:
            """
            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description

    class Kettle(PropertyType):
        """
        The user select a kettle which is available in the system. The value of this variable will be the kettle id
        """

        def __init__(self, label, description=""):
            """

            :param label:
            :param description:
            """

            PropertyType.__init__(self)
            self.label = label
            self.configurable = True
            self.description = description
