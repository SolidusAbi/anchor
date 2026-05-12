"""
Core review logic for handling file diffs and comments
"""
from dataclasses import dataclass, field
from pathlib import Path
from difflib import unified_diff
from typing import List, Optional
from datetime import datetime
from enum import StrEnum

class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


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
    original_content: List[str]
    new_content: List[str]
    diff_hunks: List[str] = field(default_factory=list)
    comments: List[LineComment] = field(default_factory=list)
    
    def __post_init__(self):
        """Generate unified diff after initialization"""
        self._generate_diff()
    
    def _generate_diff(self):
        """Generate unified diff between original and new content"""
        self.diff_hunks = list(unified_diff(
            self.original_content,
            self.new_content,
            fromfile=f"a/{self.filepath}",
            tofile=f"b/{self.filepath}",
            lineterm=""
        ))
    
    def get_display_lines(self) -> List[dict]:
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
                    "prefix": "+"
                })
                current_line_num += 1
            elif line.startswith("-") and not line.startswith("---"):
                display.append({
                    "line_number": current_line_num,
                    "content": line[1:],
                    "type": "remove",
                    "prefix": "-"
                })
            elif line.startswith(" "):
                display.append({
                    "line_number": current_line_num + 1,
                    "content": line[1:],
                    "type": "context",
                    "prefix": " "
                })
                current_line_num += 1
            elif not line.startswith("\\"):
                # Handle lines that don't have standard prefix
                current_line_num += 1
        
        return display
    
    def add_comment(self, line_number: int, comment: str, severity: Severity = Severity.INFO):
        """Add a comment to a specific line"""
        display_lines = self.get_display_lines()
        line_content = ""
        
        for line in display_lines:
            if line["line_number"] == line_number:
                line_content = line["content"]
                break
        
        self.comments.append(LineComment(
            line_number=line_number,
            original_text=line_content,
            comment=comment,
            severity=severity
        ))
    
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


@dataclass
class CodeReview:
    """Main review session"""
    files: dict[str, FileDiff] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    def load_file(self, filepath: str, original_path: Optional[str] = None):
        """
        Load a file for review.
        If original_path is provided, use it for comparison. Otherwise use file's git history.
        """
        file_path = Path(filepath)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        # Read new content
        new_content = file_path.read_text().split('\n')
        
        # Read original content
        if original_path:
            original_path = Path(original_path)
            if original_path.exists():
                original_content = original_path.read_text().split('\n')
            else:
                original_content = []
        else:
            # Try to get from git
            try:
                import subprocess
                result = subprocess.run(
                    ["git", "show", f"HEAD:{filepath}"],
                    cwd=str(file_path.parent),
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    original_content = result.stdout.split('\n')
                else:
                    original_content = []
            except Exception:
                original_content = []
        
        self.files[filepath] = FileDiff(
            filepath=filepath,
            original_content=original_content,
            new_content=new_content
        )
    
    def generate_review_md(self) -> str:
        """Generate complete REVIEW.md"""
        md = f"# Code Review\n\n"
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
        
        md += f"## Summary\n\n"
        md += f"**Total Comments:** {total_comments}\n"
        md += f"- ❌ Errors: {error_count}\n"
        md += f"- ⚠️ Warnings: {warning_count}\n"
        md += f"- ℹ️ Infos: {info_count}\n\n"
        
        # Comments per file
        md += f"## Comments\n\n"
        for file_diff in self.files.values():
            file_md = file_diff.to_markdown()
            if file_md:
                md += file_md
        
        return md
    
    def save_review(self, output_path: str = "REVIEW.md"):
        """Save review to markdown file"""
        review_content = self.generate_review_md()
        Path(output_path).write_text(review_content)
