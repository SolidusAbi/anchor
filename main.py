#!/usr/bin/env python3
"""
AI Code Review TUI - Review code diffs interactively with line-level comments
"""
import sys
import argparse
from pathlib import Path
from textual.app import ComposeResult, App
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, Button, Select
from textual.binding import Binding
from rich.panel import Panel
from rich.text import Text

from review import CodeReview, FileDiff
from tui import ReviewScreen


class FileSelector(Static):
    """Widget to select which file to review"""
    pass


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


def load_files_for_review(file_paths: list[str], original_paths: list[str] | None = None):
    """Load files into review object"""
    review = CodeReview()
    
    for i, filepath in enumerate(file_paths):
        original_path = None
        if original_paths and i < len(original_paths):
            original_path = original_paths[i]
        
        review.load_file(filepath, original_path)
    
    return review


def main():
    parser = argparse.ArgumentParser(
        description="AI Code Review - Interactive TUI for reviewing code diffs"
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="File(s) to review"
    )
    parser.add_argument(
        "-o", "--original",
        action="append",
        help="Original file(s) for comparison (if not using git)"
    )
    parser.add_argument(
        "--output",
        default="REVIEW.md",
        help="Output file for review (default: REVIEW.md)"
    )
    
    args = parser.parse_args()
    
    # Validate files exist
    for filepath in args.files:
        if not Path(filepath).exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
    
    # Load files for review
    try:
        review = load_files_for_review(args.files, args.original)
    except Exception as e:
        print(f"Error loading files: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run TUI
    app = MainApp(review)
    app.run()


if __name__ == "__main__":
    main()
