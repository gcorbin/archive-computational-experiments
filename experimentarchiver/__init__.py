class Version:

    def __init__(self, major=0, minor=0):
        if not isinstance(major, int) or not isinstance(minor, int):
            raise TypeError('Major and minor version numbers must be integers.')
        self._version_tuple = (major, minor)

    def major(self):
        return self._version_tuple[0]

    def minor(self):
        return self._version_tuple[1]

    def is_release(self):
        return self.minor() == 0

    def __le__(self, other):
        if not isinstance(other, Version):
            raise TypeError('Comparing a Version with another object is not supported.')
        # use lexicographic ordering of tuples:
        return self._version_tuple <= other._version_tuple

    def __ge__(self, other):
        return other.__le__(self)

    def __eq__(self, other):
        return self.__le__(other) and other.__le__(self)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.__le__(other) and not other.__le__(self)

    def __gt__(self, other):
        return other.__lt__(self)

    def __str__(self):
        return "{0}.{1}".format(self.major(), self.minor())

    def get_version_tuple(self):
        return self._version_tuple


version = Version(1, 0)
