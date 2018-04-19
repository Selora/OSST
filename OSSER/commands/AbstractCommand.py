class AbstractCommand:

    class AbstractArgs:
        """Shortcut to pretty-print and handle command arguments"""

        def __repr__(self):
            return self.__dict__

        def __str__(self):
            return str(self.__repr__())

    def __init__(self):
        self._commands = []
        self.executed = False
        self._results = None

    @property
    def results(self):
        return self._results

    def add(self, command: 'AbstractCommand'):
        self._commands += [command]

    def children(self):
        return self._commands

    def execute(self):
        raise NotImplementedError()

    ###############################
    # Decorators
    # Usage:
    #   Use @composite_command if the inherited class should be treated as a composite
    #   use @leaf_command if the inherited class should be treated as a leaf

    @staticmethod
    def composite_command(function_to_decorate):
        """
        Using this as a decorator will go depth-first through all children commands
        EX:

            # A child class implementing execute

            @AbtractCommand.composite_command
            def execute(self):
                ...

            If this object contains 2 child, the first containing 3 child, the second containing 1,
            it should looks like this:

            self.child[0].execute()
            self.child[0].child[0].execute()
            self.child[0].child[1].execute()
            self.child[0].child[2].execute()
            self.child[1].execute()
        """
        def wrapper(self, *args, **kwargs):
            output = function_to_decorate(self, *args, **kwargs)

            for child in self.children():
                # If the child is also a composite_command, will execute child's children
                if not child.executed:
                    child.execute()

            self.executed = True

            return output

        return wrapper

    @staticmethod
    def leaf_command(function_to_decorate):
        """
        Does not do much other than putting in evidence that this won't go through any children (if any?!)
        """
        def wrapper(self, *args, **kwargs):
            output = None

            if not self.executed:
                output = function_to_decorate(self, *args, **kwargs)
                self.executed = True

            return output

        return wrapper
