from __future__ import annotations

import random

import pytest

from plugin.money import apply, balances, greedy, minimum, shortest, split


def test_leftover_cents_go_to_the_first_sharers_listed() -> None:
    assert split(100, [("A", 1), ("B", 1), ("C", 1)]) == [("A", 34), ("B", 33), ("C", 33)]
    assert split(1, [("A", 1), ("B", 1), ("C", 1)]) == [("A", 1), ("B", 0), ("C", 0)]
    assert split(7, [("N", 2), ("M", 1)]) == [("N", 5), ("M", 2)]


def test_a_refund_is_split_like_its_size_then_negated() -> None:
    assert split(-100, [("A", 1), ("B", 1), ("C", 1)]) == [("A", -34), ("B", -33), ("C", -33)]


def expense(paid_by: str, amount: int, *sharers) -> dict:
    return {"paid_by": paid_by, "amount_cents": amount, "shares": [{"member": m, "weight": w} for m, w in sharers]}


def test_balances_are_paid_minus_owed_and_add_up_to_zero() -> None:
    owed = balances(["A", "B", "C"], [expense("A", 100, ("A", 1), ("B", 1), ("C", 1)), expense("C", 30, ("B", 1))])
    assert owed == {"A": 66, "B": -63, "C": -3}
    assert sum(owed.values()) == 0


def test_a_payment_moves_the_payer_up_and_the_payee_down() -> None:
    assert apply({"A": 50, "B": -50}, [("B", "A", 50)]) == {"A": 0, "B": 0}


def random_balances(rng: random.Random, members: int) -> dict[str, int]:
    values = [rng.choice([-1, 1]) * rng.randint(1, 6) * 5 for _ in range(members - 1)]
    values.append(-sum(values))
    return {f"m{k}": value for k, value in enumerate(values)}


@pytest.mark.parametrize("seed", range(100))
def test_greedy_and_shortest_settle_and_shortest_is_the_minimum(seed: int) -> None:
    owed = random_balances(random.Random(seed), random.Random(seed).randint(2, 8))
    for plan in (greedy(owed), shortest(owed)):
        assert not any(apply(owed, plan).values())
    assert len(shortest(owed)) == minimum(list(owed.values())) <= len(greedy(owed))
