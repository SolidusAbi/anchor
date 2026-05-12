from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from anchor.core import CodeReview

from .screen import ReviewScreen


# from review import CodeReview
# from tui import ReviewScreen


class MainApp(App):
    """Main application"""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        background: $surface;
    }
    """

    def __init__(self, review: CodeReview):
        super().__init__()
        self.review = review
        self.current_file: str | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Container()
        yield Footer()

    def on_mount(self):
        """Start file selection"""
        if len(self.review.files) == 1:
            # If only one file, go straight to review
            self.current_file = list(self.review.files.keys())[0]
            self.push_screen(ReviewScreen(self.review, self.current_file))
        else:
            # Show file selector
            self.show_file_selector()

    def show_file_selector(self):
        """Show file selection screen"""
        files = list(self.review.files.keys())
        # TODO: Implement file selector screen
        if files:
            self.current_file = files[0]
            self.push_screen(ReviewScreen(self.review, self.current_file))
