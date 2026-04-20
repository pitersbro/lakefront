import typer
from rich.console import Console

from lakefront import core

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
    core.initialize()
    console.print("[bold green]Initialization complete![/]")


@app.command()
def version():
    console.print(f"[white]{core.get_version()}[/]")


@app.command()
def ui(
    project: str = typer.Option(..., "--project", "-p", help="Project to open"),
):
    from lakefront.log import configure_for_tui
    from lakefront.tui.app import LakefrontApp

    try:
        ctx = core.get_project(project)
        configure_for_tui(ctx.log_file)
    except core.ProjectNotFoundError as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)

    LakefrontApp(ctx).run()
