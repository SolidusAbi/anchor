# AI Code Review TUI

An interactive terminal UI for reviewing code changes with line-level comments and AI feedback integration.

## Features

- 📄 **Visual Diff Display**: Shows modified files with added/removed/context lines clearly highlighted
- 💬 **Line-Level Comments**: Add comments to specific lines with severity levels (info, warning, error)
- 📝 **Buffered Comments**: All comments are held in a buffer until you explicitly save
- 📋 **REVIEW.md Generation**: Automatically generates a markdown review file in a consistent format
- ⌨️ **Keyboard Navigation**: Easy navigation with keybindings

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Review a single file with changes:

```bash
python main.py path/to/modified_file.py
```

The tool will automatically detect the original version from git history.

### Specify Original File

If not using git:

```bash
python main.py path/to/new_file.py -o path/to/original_file.py
```

### Review Multiple Files

```bash
python main.py file1.py file2.py file3.py
```

### Custom Output File

```bash
python main.py file.py --output MyReview.md
```

## Keyboard Controls

| Key | Action |
|-----|--------|
| `c` | Add comment on selected line |
| `n` | Next change |
| `p` | Previous change |
| `s` | Save review to REVIEW.md |
| `q` | Quit without saving |

## REVIEW.md Format

The generated REVIEW.md follows this structure:

```markdown
# Code Review

**Generated:** 2024-01-20T10:30:00

## Summary
- ❌ Errors: 2
- ⚠️ Warnings: 3
- ℹ️ Infos: 1

## Comments

## File: src/main.py

### Line 45 (function signature)
**Severity:** `error`
I don't like this signature. Why not use named parameters?

### Line 32 (class responsibilities)  
**Severity:** `warning`
This class has too many responsibilities. Consider splitting it.
```

## Workflow

1. Run the tool on modified files
2. Navigate through changes with `n`/`p`
3. Press `c` to add comments on selected lines
4. Choose severity (info/warning/error)
5. Type your comment and confirm
6. Repeat for all issues
7. Press `s` to save to REVIEW.md
8. Share the review with the AI for iteration

## Example

```bash
# Start review
python main.py src/auth.ts

# In the TUI:
# - Press 'n' to move through changes
# - Press 'c' on a problematic line
# - Add comment: "This class has too many responsibilities"
# - Select "warning" severity
# - Press 's' to save
```

## Architecture

- **review.py**: Core diff parsing and comment management
- **tui.py**: Textual-based UI components
- **main.py**: CLI entry point and application setup

## Future Enhancements

- [ ] Multi-file review management
- [ ] Comment editing/deletion
- [ ] Search/filter comments
- [ ] Integration with AI models for auto-suggestions
- [ ] Color theme customization
- [ ] Export to other formats (JSON, HTML)
