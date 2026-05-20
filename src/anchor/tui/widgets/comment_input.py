from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Button, Input, Label, Select, Static

from anchor.core import Severity


class CommentInput(Static):
    """Widget for inputting comments"""

    DEFAULT_CSS = """
    CommentInput {
        height: auto;
        border: solid $primary;
        padding: 1;
    }
    """

    class Added(Message):
        """Message emitted when a comment is added"""
        def __init__(self, comment: str, severity: str):
            self.comment: str = comment
            self.severity: Severity = Severity(severity)
            super().__init__()
    
    class Cancelled(Message):
        """Message emitted when comment input is cancelled"""
        pass

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

    @on(Button.Pressed, "#add-btn")
    def comment_added(self):
        comment_text = self.query_one("#comment-text", Input).value
        severity_select = self.query_one("#comment-severity", Select)
        severity = severity_select.value

        self.post_message(self.Added(
            comment=comment_text,
            severity=severity,
        ))

    @on(Button.Pressed, "#cancel-btn")
    def cancel_comment(self):
        self.post_message(self.Cancelled())
