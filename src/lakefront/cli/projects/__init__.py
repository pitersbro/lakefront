import typer
from rich.console import Console
from rich.table import Table

from lakefront import core, models

svc = core.ProjectConfigurationService

source_cli = typer.Typer(
    name="source", help="Attach, remove and sync a project's data sources."
)
projects_cli = typer.Typer(
    name="projects", help="Create, inspect and manage projects."
)
console = Console()

projects_cli.add_typer(source_cli)


@projects_cli.command(name="list", help="List all projects.")
def list_projects():
    names = svc.list_projects()
    if not names:
        console.print("[yellow]No projects found.[/]")
        return
    for name in names:
        console.print(f"  {name}")


@projects_cli.command(name="create", help="Create a new project.")
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    description: str = typer.Option(
        "", "--description", "-d", help="Human-readable project description"
    ),
    profile: str = typer.Option(
        "default", "--profile", "-p", help="Config profile to pin the project to"
    ),
):
    try:
        project = svc.create(name, description=description, profile=profile)
        console.print(
            f"[bold green]Created project '{project.name}' (profile: {project.profile})[/]"
        )
    except core.ProjectExistsError as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)


@projects_cli.command(name="inspect", help="Show a project's metadata and source count.")
def inspect_project(
    name: str = typer.Argument(..., help="Project name"),
):
    try:
        project = svc.get(name)
    except core.ProjectNotFoundError as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)

    table = Table(title=f"Project: {project.name}", show_header=True)
    table.add_column("Key", style="cyan")
    table.add_column("Value")

    table.add_row("description", project.description or "-")
    table.add_row("profile", project.profile)
    table.add_row("created_at", str(project.created_at))
    table.add_row("updated_at", str(project.updated_at))
    table.add_row("sources", str(len(project.sources)))

    console.print(table)


@projects_cli.command(name="delete", help="Delete a project (prompts for confirmation).")
def delete_project(
    name: str = typer.Argument(..., help="Project name"),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    if not confirm:
        typer.confirm(f"Delete project '{name}'?", abort=True)
    try:
        svc.delete(name)
        console.print(f"[bold green]Deleted project '{name}'.[/]")
    except core.ProjectNotFoundError as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)


@source_cli.command(name="add", help="Attach a data source (local path or s3:// URI) to a project.")
def add_source(
    project: str = typer.Option(..., "--project", "-p", help="Target project name"),
    name: str = typer.Option(..., "--name", "-n", help="Name for the source (SQL view)"),
    uri: str = typer.Option(..., "--uri", "-u", help="Source URI; scheme inferred (file/s3)"),
    description: str = typer.Option(
        "", "--description", "-d", help="Optional source description"
    ),
):
    try:
        source = models.DataSource(name=name, uri=uri, description=description)
        svc.add_source(project, source)
        console.print(f"[bold green]Added source '{name}' to '{project}'.[/]")
    except (core.ProjectNotFoundError, core.SourceExistsError) as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)


@source_cli.command(name="remove", help="Detach a data source from a project.")
def remove_source(
    project: str = typer.Option(..., "--project", "-p", help="Target project name"),
    name: str = typer.Option(..., "--name", "-n", help="Name of the source to remove"),
):
    try:
        svc.remove_source(project, name)
        console.print(f"[bold green]Removed source '{name}' from '{project}'.[/]")
    except (core.ProjectNotFoundError, core.SourceNotFoundError) as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)


@source_cli.command(name="sync", help="Sync a project's sources from the given paths.")
def sync_sources(
    project: str = typer.Option(..., "--project", "-p", help="Target project name"),
    paths: list[str] = typer.Argument(..., help="Source paths to sync"),
):
    print(project)
    print(paths)
