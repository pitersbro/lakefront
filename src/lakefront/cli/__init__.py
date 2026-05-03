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


def run_app(project: str):
    from lakefront.log import configure_for_tui
    from lakefront.tui.app import LakefrontApp

    try:
        ctx = core.get_project(project)
        configure_for_tui(ctx.log_file)
    except core.ProjectNotFoundError as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)

    LakefrontApp(ctx).run()


def run_nav():
    from lakefront.core.config import LAKEFRONT_HOME
    from lakefront.log import configure_for_tui
    from lakefront.tui.app import LakefrontApp

    log_file = LAKEFRONT_HOME / "lakefront.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    log_file.touch(exist_ok=True)
    configure_for_tui(log_file)

    LakefrontApp().run()


@app.command()
def demo():
    """Launch the built-in demo project (creates it on first run)."""
    from lakefront.core.demo import ensure_demo_project

    console.print("[bold green]Setting up demo project...[/]")
    ensure_demo_project()
    run_app("demo")


@app.command()
def ui(
    project: str = typer.Option(
        None, "--project", "-p", help="Project to open (shows navigation screen if omitted)"
    ),
):
    if project:
        run_app(project)
    else:
        run_nav()
