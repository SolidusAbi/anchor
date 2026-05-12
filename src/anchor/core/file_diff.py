from dataclasses import dataclass, field
from datetime import datetime
from difflib import unified_diff

from .types import Severity


@dataclass
class LineComment:
    """A comment on a specific line"""

    line_number: int
    original_text: str
    comment: str
    severity: Severity = Severity.INFO
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class FileDiff:
    """Represents a file diff with metadata"""

    filepath: str
    original_content: list[str]
    new_content: list[str]
    diff_hunks: list[str] = field(default_factory=list)
    comments: list[LineComment] = field(default_factory=list)

    def __post_init__(self):
        self._generate_diff()

    def _generate_diff(self):
        """Generate unified diff between original and new content"""
        self.diff_hunks = list(
            unified_diff(
                self.original_content,
                self.new_content,
                fromfile=f"a/{self.filepath}",
                tofile=f"b/{self.filepath}",
                lineterm="",
            )
        )

    def get_display_lines(self) -> list[dict]:
        """
        Get lines for display in TUI with metadata.
        Returns list of dicts with: line_number, content, type (add/remove/context)
        """
        display = []
        current_line_num = 0

        for line in self.diff_hunks:
            if line.startswith("@@"):
                # Parse hunk header to get line number
                import re

                match = re.search(r"\+(\d+)", line)
                if match:
                    current_line_num = int(match.group(1)) - 1
                continue

            if line.startswith("+++") or line.startswith("---"):
                continue

            if line.startswith("+") and not line.startswith("+++"):
                display.append({
                    "line_number": current_line_num + 1,
                    "content": line[1:],
                    "type": "add",
                    "prefix": "+",
                })
                current_line_num += 1
            elif line.startswith("-") and not line.startswith("---"):
                display.append({
                    "line_number": current_line_num,
                    "content": line[1:],
                    "type": "remove",
                    "prefix": "-",
                })
            elif line.startswith(" "):
                display.append({
                    "line_number": current_line_num + 1,
                    "content": line[1:],
                    "type": "context",
                    "prefix": " ",
                })
                current_line_num += 1
            elif not line.startswith("\\"):
                # Handle lines that don't have standard prefix
                current_line_num += 1

        return display

    def add_comment(
        self, line_number: int, comment: str, severity: Severity = Severity.INFO
    ):
        """Add a comment to a specific line"""
        display_lines = self.get_display_lines()
        line_content = ""

        for line in display_lines:
            if line["line_number"] == line_number:
                line_content = line["content"]
                break

        self.comments.append(
            LineComment(
                line_number=line_number,
                original_text=line_content,
                comment=comment,
                severity=severity,
            )
        )

    def to_markdown(self) -> str:
        """Convert review to markdown format"""
        if not self.comments:
            return ""

        md = f"## File: {self.filepath}\n\n"

        for comment in self.comments:
            md += f"### Line {comment.line_number}"
            if comment.original_text:
                md += f" ({comment.original_text[:50]})"
            md += "\n"
            md += f"**Severity:** `{comment.severity.value}`\n"
            md += f"{comment.comment}\n\n"

        return md
