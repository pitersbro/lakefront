import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer()
projects = typer.Typer()
app.add_typer(projects, name="projects")
db_app = typer.Typer()
app.add_typer(db_app, name="db")


console = Console()


@db_app.command()
def init():
    from peak.core import bootstrap

    console.print("[bold green]Initializing database...[/]")
    bootstrap()


@db_app.command()
def reset():
    from peak.core import bootstrap, teardown

    console.print("[bold red]Resetting database...[/]")
    teardown()
    console.print("[bold green]Re-initializing database...[/]")
    bootstrap()


@projects.command("list")
def list_projects():
    from peak.core import ProjectManager

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
    from peak.core import get_version

    console.print(f"[white]Peak v{get_version()} [/]")


@app.command()
def ui():
    from peak.tui import PeakApp

    PeakApp().run()
