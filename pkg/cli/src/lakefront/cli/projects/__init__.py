import typer
from lakefront import core
from rich.console import Console
from rich.table import Table

svc = core.ProjectConfigurationService

source_cli = typer.Typer(name="source")
projects_cli = typer.Typer(name="projects")
console = Console()

projects_cli.add_typer(source_cli)


@projects_cli.command(name="list")
def list_projects():
    names = svc.list_projects()
    if not names:
        console.print("[yellow]No projects found.[/]")
        return
    for name in names:
        console.print(f"  {name}")


@projects_cli.command(name="create")
def create_project(
    name: str = typer.Argument(..., help="Project name"),
    description: str = typer.Option("", "--description", "-d"),
    profile: str = typer.Option("default", "--profile", "-p"),
):
    try:
        project = svc.create(name, description=description, profile=profile)
        console.print(
            f"[bold green]Created project '{project.name}' (profile: {project.profile})[/]"
        )
    except core.ProjectExistsError as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)


@projects_cli.command(name="inspect")
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


@projects_cli.command(name="delete")
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


@source_cli.command(name="add")
def add_source(
    project: str = typer.Option(..., "--project", "-p"),
    name: str = typer.Option(..., "--name", "-n"),
    kind: str = typer.Option(..., "--kind", "-k", help="local or s3"),
    path: str = typer.Option(..., "--path"),
    description: str = typer.Option("", "--description", "-d"),
):
    try:
        source = core.DataSource(
            name=name, kind=kind, path=path, description=description
        )
        svc.add_source(project, source)
        console.print(f"[bold green]Added source '{name}' to '{project}'.[/]")
    except (core.ProjectNotFoundError, core.SourceExistsError) as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)


@source_cli.command(name="remove")
def remove_source(
    project: str = typer.Option(..., "--project", "-p"),
    name: str = typer.Option(..., "--name", "-n"),
):
    try:
        svc.remove_source(project, name)
        console.print(f"[bold green]Removed source '{name}' from '{project}'.[/]")
    except (core.ProjectNotFoundError, core.SourceNotFoundError) as e:
        console.print(f"[bold red]{e}[/]")
        raise typer.Exit(1)
