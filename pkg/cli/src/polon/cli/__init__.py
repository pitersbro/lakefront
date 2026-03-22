import typer

app = typer.Typer()


@app.command()
def explore():
    from polon.tui import PolonApp

    PolonApp().run()
