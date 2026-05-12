"""
Typer CLI entrypoint for Anchor.
"""

import typer

from anchor.cli.commands.run import run_command


app = typer.Typer(
    name="anchor",
    help="Anchor - My AI review tool for human-in-the-loop workflows",
    add_completion=False,
)

app.command(name="test")(lambda: print("Hello from Anchor!"))
app.command(name="run")(run_command)

if __name__ == "__main__":
    app()
