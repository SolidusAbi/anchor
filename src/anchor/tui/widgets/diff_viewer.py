from rich.text import Text
from textual.widgets import Static

from anchor.core import FileDiff


class DiffViewer(Static):
    """Widget to display file diff"""

    DEFAULT_CSS = """
    DiffViewer {
        border: solid $primary;
        width: 1fr;
        height: 1fr;
        overflow: auto;
    }
    """

    def __init__(self, file_diff: FileDiff, name: str = "diff"):
        super().__init__(name=name)
        self.file_diff = file_diff
        self.selected_line: int | None = None
        self.display_lines: list[dict] = []
        self.render_diff()

    def render_diff(self):
        """Render the diff view"""
        self.display_lines = self.file_diff.get_display_lines()

        if not self.display_lines:
            self.update("No changes in this file")
            return

        content = Text()

        for line in self.display_lines:
            line_num = line["line_number"]
            file_content = line["content"][:100]

            if line["type"] == "add":
                color = "green"
                symbol = "+"
            elif line["type"] == "remove":
                color = "red"
                symbol = "x"
            else:
                color = "white"
                symbol = " "

            is_selected = line_num == self.selected_line
            style = f"{color} bold reverse" if is_selected else color
            marker = "▶" if is_selected else " "

            line_text = f"{marker}{symbol} {line_num:4d} | {file_content}\n"
            content.append(line_text, style=style)

        if self.file_diff.comments:
            content.append("\n" + "=" * 60 + "\n", style="dim")
            content.append("📝 Comments:\n", style="bold cyan")

            for comment in self.file_diff.comments:
                content.append(f"  Line {comment.line_number}: ", style="bold")
                content.append(f"{comment.comment}\n", style="dim")

        self.update(content)

    def on_mouse_down(self, event) -> None:
        """Select a line with the mouse"""
        line_index = event.y
        if line_index < 0 or line_index >= len(self.display_lines):
            return

        line = self.display_lines[line_index]
        if line["type"] not in {"add", "remove"}:
            return

        self.selected_line = line["line_number"]
        if hasattr(self.screen, "current_line"):
            self.screen.current_line = self.selected_line  # type: ignore
        self.render_diff()
        self.focus()
