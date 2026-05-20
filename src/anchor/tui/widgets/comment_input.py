from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Label, Static, TextArea

from anchor.core import Severity


class CommentInput(Static):
    """Widget for inputting comments"""

    BINDINGS = [
        ("ctrl+space", "add", "Add comment"),
        ("escape", "cancel", "Cancel"),
        ("ctrl+1", "severity_info", "Severity: info"),
        ("ctrl+2", "severity_warning", "Severity: warning"),
        ("ctrl+3", "severity_error", "Severity: error"),
    ]

    DEFAULT_CSS = """
    CommentInput {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    CommentInput.severity-info {
        border: solid $primary;
    }

    CommentInput.severity-warning {
        border: solid $warning;
    }

    CommentInput.severity-error {
        border: solid $error;
    }

    CommentInput #comment-severity {
        height: 1;
    }

    CommentInput.severity-info #comment-severity {
        color: $primary;
    }

    CommentInput.severity-warning #comment-severity {
        color: $warning;
    }

    CommentInput.severity-error #comment-severity {
        color: $error;
    }

    CommentInput #comment-text {
        height: 5;
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._severity: str = "info"

    def compose(self) -> ComposeResult:
        yield Label("Comment (Ctrl+Enter to add, Esc to cancel):")
        yield Label("Severity: Info (Ctrl+1/2/3)", id="comment-severity")
        yield TextArea(id="comment-text")

    def on_mount(self) -> None:
        self._apply_severity_styles()

    def _apply_severity_styles(self) -> None:
        for severity in ("info", "warning", "error"):
            self.set_class(severity == self._severity, f"severity-{severity}")
        severity_label = self.query_one("#comment-severity", Label)
        severity_label.update(
            f"Severity: {self._severity.title()} (Ctrl+1/2/3)"
        )

    @property
    def severity(self) -> str:
        return self._severity

    def _set_severity(self, severity: str) -> None:
        self._severity = severity
        self._apply_severity_styles()

    def action_severity_info(self) -> None:
        self._set_severity("info")

    def action_severity_warning(self) -> None:
        self._set_severity("warning")

    def action_severity_error(self) -> None:
        self._set_severity("error")

    def action_add(self) -> None:
        comment_text = self.query_one("#comment-text", TextArea).text
        self.post_message(
            self.Added(
                comment=comment_text,
                severity=self._severity,
            )
        )

    def action_cancel(self) -> None:
        self.post_message(self.Cancelled())
