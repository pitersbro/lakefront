import typer
from rich.console import Console
from rich.table import Table

from lakefront import core

svc = core.ProfileConfigurationService

config_cli = typer.Typer(
    name="config", help="Manage configuration profiles (dev / staging / prod)."
)
console = Console()


@config_cli.command(name="list", help="List all configuration profiles.")
def list_profiles():
    profiles = svc.list_profiles()

    console.print("[bold green]Listing all profiles...[/]")
    console.print(profiles)


@config_cli.command(help="Show Lakefront config directories and paths.")
def info():
    info = svc.info()
    table = Table(title="Configuration Service Info", show_header=True)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    for key, value in info.items():
        table.add_row(key, str(value))
    console.print(table)


@config_cli.command(name="create", help="Create a new configuration profile.")
def create_profile(
    profile: str = typer.Option(
        ..., "--profile", "-p", help="The name of the profile to create."
    ),
):
    console.print(f"[bold green]Creating profile '{profile}'...[/]")
    try:
        path = svc.create_profile(profile)
        console.print(f"[bold green]Profile created at: {path}[/]")
    except FileExistsError as e:
        console.print(f"[bold red]{e}[/]")


@config_cli.command(name="delete", help="Delete a configuration profile.")
def delete_profile(
    profile: str = typer.Option(
        ..., "--profile", "-p", help="The name of the profile to delete."
    ),
):
    console.print(f"[bold green]Deleting profile '{profile}'...[/]")
    try:
        if profile in svc.list_profiles():
            typer.confirm(
                f"Are you sure you want to delete profile '{profile}'?", abort=True
            )

        svc.delete_profile(profile)
        console.print(f"[bold green]Profile '{profile}' deleted.[/]")
    except FileNotFoundError as e:
        console.print(f"[bold red]{e}[/]")


@config_cli.command(help="Inspect a profile's current settings.")
def inspect(
    profile: str = typer.Option(
        None,
        "--profile",
        "-p",
        help="The name of the profile to inspect. If not provided, lists all profiles.",
    ),
):
    profile = profile or svc.get_active_profile()
    console.print(f"[bold green]Inspecting profile '{profile}'...[/]")
    try:
        config = svc.inspect_profile(profile)
    except FileNotFoundError:
        console.print(f"[bold red]Profile '{profile}' not found.[/]")
        raise typer.Exit()
    table = Table(title=f"Profile: {profile}", show_header=True)
    table.add_column("Section", style="cyan")
    table.add_column("Key", style="green")
    table.add_column("Value")
    for section, values in config.items():
        for i, (key, value) in enumerate(values.items()):
            table.add_row(
                section if i == 0 else "",  # only show section name once
                key,
                str(value),
            )

    console.print(table)


@config_cli.command(name="get-active", help="Show which profile is currently active.")
def get_active_profile():
    name = svc.get_active_profile()
    console.print(f"[bold green]Active profile: {name}[/]")


@config_cli.command(name="set-active", help="Switch the active configuration profile.")
def set_active_profile(
    profile: str = typer.Option(
        None,
        "--profile",
        "-p",
        help="The name of the profile to set as active.",
    ),
):
    if not profile:
        console.print("[bold red]Please provide a profile to set as active.[/]")
        raise typer.Exit()

    console.print(f"[bold green]Setting active profile to '{profile}'...[/]")
    try:
        svc.set_active_profile(profile)
        console.print(f"[bold green]Active profile set to: {profile}[/]")
    except ValueError:
        console.print(f"[bold red]Profile '{profile}' not found.[/]")
