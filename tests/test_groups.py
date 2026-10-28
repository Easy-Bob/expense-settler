from __future__ import annotations

import pytest

from contract import Group
from plugin.groups import DATA
from plugin.money import greedy
from plugin.tools_dev.build_groups import SPECS, build, serialize

SPEC = {spec.group: spec for spec in SPECS}


@pytest.mark.parametrize("group", list(Group))
def test_the_bundled_group_is_what_the_generator_builds(group: Group) -> None:
    assert (DATA / f"{group.value}.json").read_text() == serialize(build(SPEC[group]))


@pytest.mark.parametrize("group", list(Group))
def test_the_answer_key_is_the_specs(group: Group, pinned: dict) -> None:
    key = pinned[group]
    assert key.minimum == SPEC[group].minimum
    assert len(greedy({b.member: b.cents for b in key.balances})) == SPEC[group].greedy
    assert sum(b.cents for b in key.balances) == 0


def test_some_groups_beat_the_greedy_plan() -> None:
    assert [spec.group for spec in SPECS if spec.greedy > spec.minimum] == [Group.TRIP, Group.CLUB]
