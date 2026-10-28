"""The fewest-payments DP against a brute force that tries every way to split the members into groups."""

from __future__ import annotations

import random

import pytest

from plugin.money import minimum


def partitions(items: list[int]):
    """Every way to split ``items`` into non-empty groups."""
    if not items:
        yield []
        return
    first, rest = items[0], items[1:]
    for split in partitions(rest):
        yield [[first], *split]
        for k in range(len(split)):
            yield [*split[:k], [first, *split[k]], *split[k + 1 :]]


def brute_force(values: list[int]) -> int:
    """The fewest payments: n minus the most groups adding up to 0, over every partition."""
    nonzero = [value for value in values if value]
    if not nonzero:
        return 0
    best = max(
        sum(1 for group in split if sum(group) == 0) for split in partitions(nonzero) if all(sum(g) == 0 for g in split)
    )
    return len(nonzero) - best


@pytest.mark.parametrize("seed", range(200))
def test_minimum_matches_brute_force(seed: int) -> None:
    rng = random.Random(seed)
    values = [rng.choice([-1, 1]) * rng.randint(0, 4) for _ in range(rng.randint(1, 7))]
    values.append(-sum(values))
    assert minimum(values) == brute_force(values)


def test_known_minimums() -> None:
    assert minimum([]) == 0
    assert minimum([0, 0, 0]) == 0
    assert minimum([5, -5]) == 1
    assert minimum([30, 20, -30, -20]) == 2
    assert minimum([3, 1, -2, -2]) == 3
