import pytest

from contract import Group, SettleInput
from plugin import pin_settlement


@pytest.fixture(scope="session")
def pinned(tmp_path_factory: pytest.TempPathFactory) -> dict:
    """Each group's answer key, as NanoAgent pins it before the agent starts."""
    return {group: pin_settlement(SettleInput(group=group), tmp_path_factory.mktemp(group.value)) for group in Group}
