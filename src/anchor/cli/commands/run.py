from typing import Annotated

import typer

from anchor.core import CodeReview
from anchor.tui.app import MainApp


def load_files_for_review(
    file_paths: list[str], original_paths: list[str] | None = None
) -> CodeReview:
    """Load files into review object

    Returns:
        CodeReview: If files were loaded successfully.
        None: If any file was not found.
    """
    review = CodeReview()

    for i, filepath in enumerate(file_paths):
        try:
            original_path = None
            if original_paths and i < len(original_paths):
                original_path = original_paths[i]

            review.load_file(filepath, original_path)
        except FileNotFoundError as f:
            typer.secho(f, fg=typer.colors.RED, err=True)
            raise typer.Exit(code=1)

    return review


def run_command(
    file: str,
    original: Annotated[
        str | None,
        typer.Option(
            "-o",
            "--original",
            help="original file for comparison (if not using git)",
        ),
    ] = None,
):
    """
    Launch interactive TUI review for a file.
    """
    if original:
        print(f"Running review for {file} with original {original}")
    else:
        print(f"Running review for {file} without original")

    try:
        review = load_files_for_review([file], [original] if original else None)
        app = MainApp(review)
        app.run()
    except Exception:
        raise typer.Exit(code=1)
