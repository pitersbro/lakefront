import pytest

from lakefront import core
from lakefront.tui.app import LakefrontApp
from lakefront.tui.modals.confirm import ConfirmModal
from lakefront.tui.modals.source_attach import SourceAttachModal
from lakefront.tui.screens.navigation import NavigationScreen
from lakefront.tui.screens.project import ProjectScreen
from lakefront.tui.widgets.source_pane import SourceItem, SourcePane


@pytest.fixture(scope="module")
def ctx():
    yield core.get_project("test-project")


@pytest.mark.asyncio
async def test_app_initialization(ctx):
    async with LakefrontApp(ctx).run_test() as pilot:
        assert pilot.app.ctx == ctx
        assert pilot.app.sub_title.startswith("Lakehouse Observability Platform - v")
        assert pilot.app.theme == ctx.settings.core.theme or app.theme == "tokyo-night"


@pytest.mark.asyncio
async def test_app_project_screen_mounted(ctx):
    async with LakefrontApp(ctx).run_test() as pilot:
        await pilot.pause()
        assert len(pilot.app.screen_stack) == 2
        assert isinstance(pilot.app.screen, ProjectScreen)


@pytest.mark.asyncio
async def test_source_pane(ctx):
    async with LakefrontApp(ctx).run_test() as pilot:
        await pilot.pause()
        sources = pilot.app.screen.query_one(SourcePane)
        items = sources.query("SourceItem")
        assert sources.border_title == "Sources"
        assert len(items) == len(ctx.sources)
        assert len(items) > 0


@pytest.mark.asyncio
async def test_source_attach_modal(ctx):
    async with LakefrontApp(ctx).run_test() as pilot:
        await pilot.pause()
        await pilot.press("a")
        assert isinstance(pilot.app.screen, SourceAttachModal)
        await pilot.press("escape")
        assert isinstance(pilot.app.screen, ProjectScreen)


@pytest.mark.asyncio
async def test_source_detach_modal(ctx):
    async with LakefrontApp(ctx).run_test() as pilot:
        await pilot.pause()
        await pilot.press("d")
        assert isinstance(pilot.app.screen, ConfirmModal)
        await pilot.press("escape")
        assert isinstance(pilot.app.screen, ProjectScreen)


@pytest.mark.asyncio
async def test_app_exit(ctx):
    async with LakefrontApp(ctx).run_test() as pilot:
        await pilot.pause()
        await pilot.press("q")


@pytest.mark.asyncio
async def test_source_item_shows_column_types(ctx):
    async with LakefrontApp(ctx).run_test() as pilot:
        await pilot.pause()
        source_pane = pilot.app.screen.query_one(SourcePane)
        first_item = source_pane.query(SourceItem).first()
        first_item.focus()
        await pilot.press("space")  # expand
        await pilot.pause()
        assert len(first_item._columns) > 0, "No columns fetched after expanding source"
        for col_name, col_type in first_item._columns:
            assert col_name != "", "Column name is empty"
            assert col_type != "", f"Column type is empty for column: {col_name!r}"


@pytest.mark.asyncio
async def test_navigation_screen_mounted_without_ctx():
    async with LakefrontApp().run_test() as pilot:
        await pilot.pause()
        assert isinstance(pilot.app.screen, NavigationScreen)


@pytest.mark.asyncio
async def test_navigation_screen_lists_projects():
    async with LakefrontApp().run_test() as pilot:
        await pilot.pause()
        await pilot.pause()  # allow worker to complete
        screen = pilot.app.screen
        assert isinstance(screen, NavigationScreen)
        from textual.widgets import DataTable
        table = screen.query_one("#projects-table", DataTable)
        assert table.row_count == len(core.list_projects())
