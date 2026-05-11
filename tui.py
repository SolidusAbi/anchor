"""
TUI for reviewing code diffs and adding comments
"""
from textual.app import ComposeResult, on
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, Button, Input, Select, TextArea, Label
from textual.screen import Screen
from textual.binding import Binding
from rich.text import Text
from rich.syntax import Syntax
from rich.console import Console
from rich.table import Table

from review import CodeReview, FileDiff, Severity


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
        self.render_diff()
    
    def render_diff(self):
        """Render the diff view"""
        display_lines = self.file_diff.get_display_lines()
        
        if not display_lines:
            self.update("No changes in this file")
            return
        
        # Build rich display
        from rich.panel import Panel
        content = Text()
        
        for line in display_lines:
            line_num = line["line_number"]
            prefix = line["prefix"]
            file_content = line["content"][:100]
            
            # Color based on type
            if line["type"] == "add":
                color = "green"
                symbol = "✚"
            elif line["type"] == "remove":
                color = "red"
                symbol = "✖"
            else:
                color = "white"
                symbol = " "
            
            # Highlight selected line
            is_selected = line_num == self.selected_line
            style = f"{color} bold" if is_selected else color
            
            line_text = f"{symbol} {line_num:4d} | {file_content}\n"
            content.append(line_text, style=style)
        
        # Show comments
        if self.file_diff.comments:
            content.append("\n" + "=" * 60 + "\n", style="dim")
            content.append("📝 Comments:\n", style="bold cyan")
            
            for comment in self.file_diff.comments:
                content.append(f"  Line {comment.line_number}: ", style="bold")
                content.append(f"{comment.comment}\n", style="dim")
        
        self.update(content)


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
                id="comment-severity"
            )
            yield Button("Add", id="add-btn", variant="primary")
            yield Button("Cancel", id="cancel-btn")


class ReviewScreen(Screen):
    """Main review screen"""
    
    BINDINGS = [
        Binding("c", "comment", "Comment [C]"),
        Binding("s", "save", "Save [S]"),
        Binding("n", "next_change", "Next [N]"),
        Binding("p", "prev_change", "Previous [P]"),
        Binding("q", "quit", "Quit [Q]"),
    ]
    
    def __init__(self, review: CodeReview, filepath: str):
        super().__init__()
        self.review = review
        self.filepath = filepath
        self.file_diff = review.files[filepath]
        self.current_line: int | None = None
        self.showing_comment_input = False
    
    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical():
            yield Label(f"📄 Reviewing: {self.filepath}")
            self.diff_viewer = DiffViewer(self.file_diff)
            yield self.diff_viewer
            
            self.comment_input = CommentInput(id="comment-input")
            yield self.comment_input
        
        yield Footer()
    
    def on_mount(self):
        """Setup after mount"""
        self.comment_input.display = False
        self.render_diff_info()
    
    def render_diff_info(self):
        """Update the diff view"""
        display_lines = self.file_diff.get_display_lines()
        if display_lines:
            self.current_line = display_lines[0]["line_number"]
        self.diff_viewer.render_diff()
    
    def action_comment(self):
        """Start adding a comment"""
        if not self.current_line:
            self.notify("Select a line first", severity="error")
            return
        
        self.showing_comment_input = True
        self.comment_input.display = True
        self.comment_input.query_one("#comment-text", Input).focus()
    
    def action_save(self):
        """Save the review to REVIEW.md"""
        self.review.save_review()
        self.notify("✅ Saved to REVIEW.md", severity="information")
    
    def action_next_change(self):
        """Move to next change"""
        display_lines = self.file_diff.get_display_lines()
        if not display_lines:
            return
        
        current_idx = next(
            (i for i, l in enumerate(display_lines) if l["line_number"] == self.current_line),
            -1
        )
        
        if current_idx < len(display_lines) - 1:
            self.current_line = display_lines[current_idx + 1]["line_number"]
            self.diff_viewer.selected_line = self.current_line
            self.diff_viewer.render_diff()
    
    def action_prev_change(self):
        """Move to previous change"""
        display_lines = self.file_diff.get_display_lines()
        if not display_lines:
            return
        
        current_idx = next(
            (i for i, l in enumerate(display_lines) if l["line_number"] == self.current_line),
            -1
        )
        
        if current_idx > 0:
            self.current_line = display_lines[current_idx - 1]["line_number"]
            self.diff_viewer.selected_line = self.current_line
            self.diff_viewer.render_diff()
    
    def action_quit(self):
        """Quit the application"""
        self.app.exit()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "add-btn":
            self.add_comment()
        elif event.button.id == "cancel-btn":
            self.cancel_comment()
    
    def add_comment(self):
        """Process comment addition"""
        if not self.current_line:
            return
        
        comment_text = self.comment_input.query_one("#comment-text", Input).value
        severity_select = self.comment_input.query_one("#comment-severity", Select)
        severity = Severity(severity_select.value)
        
        if comment_text:
            self.file_diff.add_comment(
                line_number=self.current_line,
                comment=comment_text,
                severity=severity
            )
            self.notify(f"✅ Comment added to line {self.current_line}")
        
        self.cancel_comment()
    
    def cancel_comment(self):
        """Cancel comment input"""
        self.showing_comment_input = False
        self.comment_input.display = False
        self.comment_input.query_one("#comment-text", Input).value = ""
        self.diff_viewer.focus()
