from dataclasses import dataclass
from enum import StrEnum


class LineType(StrEnum):
    ADD = "add"
    REMOVE = "remove"
    CONTEXT = "context"


@dataclass
class DisplayLine:
    line_number: int
    content: str
    line_type: LineType
