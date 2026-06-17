# validation.py

"""
Simple reusable validation helpers for the codebase-index project.

These helpers are deliberately tiny to avoid pulling in heavy dependencies.
They raise the same exceptions that the original code raised so behavior stays compatible.
"""

from typing import Any

def ensure_str(value: Any, name: str = "value") -> str:
    """Return `value` if it is a `str`; otherwise raise `TypeError`."""
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    return value

def ensure_positive_int(value: Any, name: str = "value") -> int:
    """Return `value` if it is a positive `int`; otherwise raise `ValueError`/`TypeError`."""
    if not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value
