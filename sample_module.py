"""Sample module for testing function extraction."""


def simple_func(a, b):
    """A simple function."""
    return a + b


def complex_func(x, y=10):
    """A function with default args and docstring."""
    result = x * y
    if result < 0:
        raise ValueError("Result cannot be negative")
    return result


class MyClass:
    """A test class."""

    def method(self):
        pass


def another_func():
    """Function after a class."""
    print("hello")
    # multiline
    # comment
    return 42