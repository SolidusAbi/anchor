"""
Shared types and enums for the anchor core module.
"""

from enum import StrEnum


class Severity(StrEnum):
    """Comment severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
