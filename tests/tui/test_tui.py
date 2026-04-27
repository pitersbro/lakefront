import pytest

from lakefront import core
from lakefront.tui.app import LakefrontApp
from lakefront.tui.modals.confirm import ConfirmModal
from lakefront.tui.modals.source_attach import SourceAttachModal
from lakefront.tui.screens.project import ProjectScreen
from lakefront.tui.widgets.source_pane import SourcePane


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
