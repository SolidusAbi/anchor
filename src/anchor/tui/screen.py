"""
TUI for reviewing code diffs and adding comments
"""

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select

from anchor.core import CodeReview, Severity

from .widgets import CommentInput, DiffViewer


class ReviewScreen(Screen):
    """Main review screen"""

    BINDINGS = [
        Binding("c", "comment", "Comment [C]"),
        Binding("C", "comment", show=False),
        Binding("s", "save", "Save [S]"),
        Binding("S", "save", show=False),
        Binding("n", "next_change", "Next [N]"),
        Binding("N", "next_change", show=False),
        Binding("p", "prev_change", "Previous [P]"),
        Binding("P", "prev_change", show=False),
        Binding("j", "next_change", "Down [J]"),
        Binding("k", "prev_change", "Up [K]"),
        Binding("down", "next_change", show=False),
        Binding("up", "prev_change", show=False),
        Binding("q", "quit", "Quit [Q]"),
        Binding("Q", "quit", show=False),
    ]

    def __init__(self, review: CodeReview, filepath: str):
        super().__init__()
        self.review = review
        self.filepath = filepath
        self.file_diff = review.files[filepath]
        self.current_line: int | None = None
        self.comment_input: CommentInput | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label(f"📄x Reviewing: {self.filepath}")
            self.diff_viewer = DiffViewer(self.file_diff)
            yield self.diff_viewer

            self.comment_area = Vertical(id="comment-area")
            yield self.comment_area

        yield Footer()

    def on_mount(self):
        """Setup after mount"""
        self.render_diff_info()
        self.focus()

    def render_diff_info(self):
        """Update the diff view"""
        display_lines = self.file_diff.get_display_lines()
        change_lines = [
            line for line in display_lines if line["type"] in {"add", "remove"}
        ]
        if change_lines:
            self.current_line = change_lines[0]["line_number"]
            self.diff_viewer.selected_line = self.current_line
        self.diff_viewer.render_diff()

    async def action_comment(self):
        """Start adding a comment"""
        if self.current_line is None:
            self.notify("Select a changed line first", severity="error")
            return

        display_lines = self.file_diff.get_display_lines()
        current = next(
            (
                line
                for line in display_lines
                if line["line_number"] == self.current_line
            ),
            None,
        )
        if not current or current["type"] not in {"add", "remove"}:
            self.notify("Select a changed line first", severity="error")
            return

        if self.comment_input is None:
            self.comment_input = CommentInput(id="comment-input")
            await self.comment_area.mount(self.comment_input)

        comment_text = self.comment_input.query_one("#comment-text", Input)
        comment_text.value = ""
        comment_text.focus()

    def action_save(self):
        """Save the review to REVIEW.md"""
        self.review.save_review()
        self.notify("✅ Saved to REVIEW.md", severity="information")

    def action_next_change(self):
        """Move to next change"""
        display_lines = self.file_diff.get_display_lines()
        change_lines = [
            line for line in display_lines if line["type"] in {"add", "remove"}
        ]
        if not change_lines:
            return

        current_idx = next(
            (
                i
                for i, line in enumerate(change_lines)
                if line["line_number"] == self.current_line
            ),
            -1,
        )

        if current_idx < len(change_lines) - 1:
            self.current_line = change_lines[current_idx + 1]["line_number"]
            self.diff_viewer.selected_line = self.current_line
            self.diff_viewer.render_diff()

    def action_prev_change(self):
        """Move to previous change"""
        display_lines = self.file_diff.get_display_lines()
        change_lines = [
            line for line in display_lines if line["type"] in {"add", "remove"}
        ]
        if not change_lines:
            return

        current_idx = next(
            (
                i
                for i, line in enumerate(change_lines)
                if line["line_number"] == self.current_line
            ),
            -1,
        )

        if current_idx > 0:
            self.current_line = change_lines[current_idx - 1]["line_number"]
            self.diff_viewer.selected_line = self.current_line
            self.diff_viewer.render_diff()

    def action_quit(self):
        """Quit the application"""
        self.app.exit()

    @on(CommentInput.Added)
    async def add_comment2(self, message: CommentInput.Added):
        """Handle comment added message"""
        self.file_diff.add_comment(
            line_number=self.current_line,
            comment=message.comment,
            severity=Severity(message.severity),
        )
        
        self.notify(f"✅ Comment added to line {self.current_line}")
        await self.cancel_comment()

    # async def on_comment_input_comment_added(self, message: CommentInput.CommentAdded):
    #     """Handle comment added message"""
    #     self.file_diff.add_comment(
    #         line_number=self.current_line,
    #         comment=message.comment,
    #         severity=message.severity,
    #     )
    #     self.notify(f"✅ Comment added to line {message.line_number}")
    #     # self.render_diff_info()

    # async def on_button_pressed(self, event: Button.Pressed) -> None:
    #     """Handle button presses"""
    #     if event.button.id == "add-btn":
    #         await self.add_comment()
    #     elif event.button.id == "cancel-btn":
    #         await self.cancel_comment()

    async def add_comment(self):
        """Process comment addition"""
        if self.current_line is None or self.comment_input is None:
            return

        display_lines = self.file_diff.get_display_lines()
        current = next(
            (
                line
                for line in display_lines
                if line["line_number"] == self.current_line
            ),
            None,
        )
        if not current or current["type"] not in {"add", "remove"}:
            self.notify("Select a changed line first", severity="error")
            return

        comment_text = self.comment_input.query_one("#comment-text", Input).value
        severity_select = self.comment_input.query_one("#comment-severity", Select)
        severity = Severity(severity_select.value)

        if comment_text:
            self.file_diff.add_comment(
                line_number=self.current_line,
                comment=comment_text,
                severity=severity,
            )
            self.notify(f"✅ Comment added to line {self.current_line}")

        await self.cancel_comment()

    @on(CommentInput.Cancelled)
    async def cancel_comment(self):
        """Cancel comment input"""
        if self.comment_input is not None:
            self.comment_input.query_one("#comment-text", Input).value = ""
            await self.comment_input.remove()
            self.comment_input = None
        self.diff_viewer.focus()
