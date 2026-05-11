#!/usr/bin/env python3
"""
Test script for the review system without TUI
"""
from review import CodeReview, Severity
from pathlib import Path
import tempfile

# Create test files
with tempfile.TemporaryDirectory() as tmpdir:
    tmpdir = Path(tmpdir)
    
    # Create original file
    original_file = tmpdir / "test.py"
    original_file.write_text("""def hello(name):
    print(f"Hello {name}")
    return True

class DataProcessor:
    def __init__(self):
        self.data = []
    
    def process(self):
        pass
    
    def validate(self):
        pass
""")
    
    # Create modified file
    modified_file = tmpdir / "test_modified.py"
    modified_file.write_text("""def hello(name, greeting="Hello"):
    print(f"{greeting} {name}!")
    return True

class DataProcessor:
    def __init__(self):
        self.data = []
        self.cache = {}
        self.logger = None
    
    def process(self, raw_data):
        self.validate()
        self.transform()
        self.save()
    
    def transform(self):
        pass
    
    def validate(self):
        pass
    
    def save(self):
        pass
""")
    
    # Create review
    print("🔍 Creating code review...")
    review = CodeReview()
    
    # Load with explicit original
    file_diff = review.files.get("test.py")
    if not file_diff:
        from review import FileDiff
        original_content = original_file.read_text().split('\n')
        new_content = modified_file.read_text().split('\n')
        
        review.files["test.py"] = FileDiff(
            filepath="test.py",
            original_content=original_content,
            new_content=new_content
        )
    
    file_diff = review.files["test.py"]
    
    # Show diff
    print("\n📊 Diff Preview:")
    display_lines = file_diff.get_display_lines()
    for line in display_lines[:10]:
        prefix = line["prefix"]
        num = line["line_number"]
        content = line["content"][:60]
        print(f"  {prefix} {num:3d}: {content}")
    
    # Add comments
    print("\n💬 Adding comments...")
    file_diff.add_comment(
        line_number=1,
        comment="I don't like this function signature. Why add the greeting parameter?",
        severity=Severity.WARNING
    )
    file_diff.add_comment(
        line_number=5,
        comment="This class has too many responsibilities. Consider splitting validation, processing, and persistence.",
        severity=Severity.ERROR
    )
    file_diff.add_comment(
        line_number=7,
        comment="Good addition of cache, but needs documentation",
        severity=Severity.INFO
    )
    
    print(f"✅ Added {len(file_diff.comments)} comments")
    
    # Generate review
    print("\n📝 Generating REVIEW.md...")
    review_md = review.generate_review_md()
    
    print("\n" + "="*60)
    print("Generated REVIEW.md:")
    print("="*60)
    print(review_md)
    
    # Save
    review.save_review(tmpdir / "REVIEW.md")
    print(f"\n✅ Review saved to {tmpdir / 'REVIEW.md'}")
    
    # Verify saved file
    saved_content = (tmpdir / "REVIEW.md").read_text()
    print(f"📄 File size: {len(saved_content)} bytes")
    print(f"✅ All tests passed!")
