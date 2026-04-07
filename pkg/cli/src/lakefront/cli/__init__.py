import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
projects = typer.Typer()
app.add_typer(projects, name="projects")
db_app = typer.Typer()
app.add_typer(db_app, name="db")


console = Console()


@db_app.command(
    help="Initialize the lakefront database. Run this command before using any other commands."
)
def init():
    from lakefront.core import bootstrap

    console.print("[bold green]Initializing database...[/]")
    bootstrap()


@db_app.command(help="Open a duckdb shell connected to the lakefront database.")
def shell():
    """Open a duckdb shell connected to the lakefront database.

    Usage:
    $ lakefront db shell
    $ db: SELECT * FROM projects;
    $ db: show tables;
    $ db: describe projects;
    $ db:.exit
    """
    import subprocess

    from lakefront.core.config import DB_PATH

    subprocess.run(["duckdb", str(DB_PATH)], check=True)


@db_app.command()
def reset():
    from lakefront.core import bootstrap, teardown

    console.print("[bold green]Re-initializing database...[/]")
    teardown()
    bootstrap()


@projects.command("list")
def list_projects():
    from lakefront.core import ProjectManager

    pm = ProjectManager()
    projects = pm.list()
    table = Table(title="Projects", show_header=True, header_style="bold white")
    table.add_column("ID", justify="right", style="white", width=6)
    table.add_column("Name", style="dim", width=30)
    table.add_column("Created At", justify="right", style="dim")
    for p in projects:
        table.add_row(str(p.id), p.name, p.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    console.print(table)


@app.command()
def version():
    from lakefront.core import get_version

    console.print(f"[white]lakefront v{get_version()} [/]")


@app.command()
def ui():
    from lakefront.tui import LakeFrontApp

    LakeFrontApp().run()
