import typer
from lakefront.core import initialize
from rich.console import Console

from .config import config_cli
from .projects import projects_cli

# from rich.table import Table

app = typer.Typer()
projects = typer.Typer()
app.add_typer(projects, name="projects")
db_app = typer.Typer()
app.add_typer(db_app, name="db")


app.add_typer(projects_cli)

app.add_typer(config_cli)
app.add_typer(projects_cli)


console = Console()


@app.command(
    help="Initialize the lakefront database. Run this command before using any other commands."
)
def init():
    console.print("[bold green]Initializing...[/]")
    initialize()
    console.print("[bold green]Initialization complete![/]")


@app.command()
def version():
    from lakefront.core import get_version

    console.print(f"[white]lakefront v{get_version()} [/]")


@app.command()
def ui(
    project: str = typer.Option(..., "--project", "-p", help="Project to open"),
):
    from lakefront.tui.app import LakefrontApp

    LakefrontApp(project).run()
