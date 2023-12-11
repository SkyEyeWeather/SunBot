"""
# Location Class

This class define a location which is essentially a name and a timezone. This
class is immutable.
"""

from operator import itemgetter

import pytz


class Location(tuple):
    """Define a location. This class is a subclass of tuple, so it is immutable
    and can be used in dictionnary as key
    """

    __slots__ = []  # To prevent creation of attributes

    def __new__(cls, location_name: str, location_tz_str: str):
        location_tz = None
        if location_tz_str != "":
            location_tz = pytz.timezone(location_tz_str)
        return tuple.__new__(cls, (location_name, location_tz))

    def __eq__(self, __value: object) -> bool:
        """Compare this location"""
        if type(__value) != type(self):
            return False
        return self.name == __value.name

    def __hash__(self) -> int:
        return self.name.__hash__()

    # Properties
    name: str = property(itemgetter(0))
    tz: str = property(itemgetter(1))
