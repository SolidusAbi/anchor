from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Button, Input, Label, Select, Static


class CommentInput(Static):
    """Widget for inputting comments"""

    DEFAULT_CSS = """
    CommentInput {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Label("Comment on line (press Enter to add, Esc to cancel):")
        yield Input(id="comment-text", placeholder="Add comment here...")
        with Horizontal():
            yield Select(
                [("ℹ️ Info", "info"), ("⚠️ Warning", "warning"), ("❌ Error", "error")],
                value="info",
                id="comment-severity",
            )
            yield Button("Add", id="add-btn", variant="primary")
            yield Button("Cancel", id="cancel-btn")
