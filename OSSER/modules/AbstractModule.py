class AbstractModule:

    class AbstractArgs:

        def __repr__(self):
            return self.__dict__

        def __str__(self):
            return str(self.__repr__())
