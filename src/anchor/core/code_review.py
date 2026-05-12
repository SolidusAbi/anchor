import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .file_diff import FileDiff
from .types import Severity


def git_retrieval(filepath: Path) -> list[str]:
    """Retrieve the original content of a file from git history"""
    try:
        result = subprocess.run(
            ["git", "show", f"HEAD:{filepath.name}"],
            cwd=str(filepath.parent),
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.split("\n")
    except subprocess.CalledProcessError:
        return []


@dataclass
class CodeReview:
    files: dict[str, FileDiff] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def load_file(self, filepath: str, original_path: str | None = None):
        """
        Load a file for review.
        If original_path is provided, use it for comparison. Otherwise use file's git
        history.

        Raises:
            FileNotFoundError: If the file to review is not found.
        """
        file_path = Path(filepath)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")

        # Read new content
        new_content = file_path.read_text().split("\n")

        # Read original content
        if original_path:
            original_path_obj = Path(original_path)
            if original_path_obj.exists():
                original_content = original_path_obj.read_text().split("\n")
            else:
                original_content = []
        else:
            # Try to get from git
            # try:
            #     import subprocess

            #     result = subprocess.run(
            #         ["git", "show", f"HEAD:{filepath}"],
            #         cwd=str(file_path.parent),
            #         capture_output=True,
            #         text=True,
            #     )
            #     if result.returncode == 0:
            #         original_content = result.stdout.split("\n")
            #     else:
            #         original_content = []
            # except Exception:
            #     original_content = []
            original_content = git_retrieval(file_path)

        self.files[filepath] = FileDiff(
            filepath=filepath,
            original_content=original_content,
            new_content=new_content,
        )

    def generate_review_md(self) -> str:
        """Generate complete REVIEW.md"""
        md = "# Code Review\n\n"
        md += f"**Generated:** {self.created_at.isoformat()}\n"
        md += f"**Files Reviewed:** {len(self.files)}\n\n"

        # Summary statistics
        total_comments = sum(len(f.comments) for f in self.files.values())
        error_count = sum(
            len([c for c in f.comments if c.severity == Severity.ERROR])
            for f in self.files.values()
        )
        warning_count = sum(
            len([c for c in f.comments if c.severity == Severity.WARNING])
            for f in self.files.values()
        )
        info_count = sum(
            len([c for c in f.comments if c.severity == Severity.INFO])
            for f in self.files.values()
        )

        md += "## Summary\n\n"
        md += f"**Total Comments:** {total_comments}\n"
        md += f"- [X] Errors: {error_count}\n"
        md += f"- [!] Warnings: {warning_count}\n"
        md += f"- [I] Infos: {info_count}\n\n"

        # Comments per file
        md += "## Comments\n\n"
        for file_diff in self.files.values():
            file_md = file_diff.to_markdown()
            if file_md:
                md += file_md

        return md

    def save_review(self, output_path: str = "REVIEW.md"):
        """Save review to markdown file"""
        review_content = self.generate_review_md()
        Path(output_path).write_text(review_content)
