from __future__ import annotations

from pathlib import Path

import pytest

from contract import BalancesInput, CheckInput, Group, Payment, ReadInput
from plugin import check_settlement, get_balances, read_expenses


def test_read_expenses_gives_the_log(tmp_path: Path) -> None:
    log = read_expenses(ReadInput(group=Group.REFUND), tmp_path)
    assert log.members == ["Rae", "Sol", "Taj", "Uma"]
    assert [e.amount_cents for e in log.expenses][:2] == [16000, -8000]


@pytest.mark.parametrize("group", list(Group))
def test_get_balances_agrees_with_the_answer_key(group: Group, tmp_path: Path, pinned: dict) -> None:
    assert get_balances(BalancesInput(group=group), tmp_path).balances == pinned[group].balances


def test_check_settlement_names_who_is_still_off(tmp_path: Path) -> None:
    def check(*payments):
        plan = [Payment(payer=p, payee=q, cents=c) for p, q, c in payments]
        return check_settlement(CheckInput(group=Group.REFUND, payments=plan), tmp_path)

    done = check(("Taj", "Rae", 4000), ("Sol", "Uma", 2000))
    assert done.settles and done.payments == 2 and done.remaining == []
    short = check(("Taj", "Rae", 3999), ("Sol", "Uma", 2000))
    assert not short.settles and [(b.member, b.cents) for b in short.remaining] == [("Rae", 1), ("Taj", -1)]


@pytest.mark.parametrize(
    ("payment", "message"),
    [
        (("Zed", "Rae", 100), "not a member"),
        (("Rae", "Rae", 100), "cannot pay themselves"),
        (("Taj", "Rae", 0), "1 cent or more"),
        (("Taj", "Rae", -5), "1 cent or more"),
    ],
)
def test_check_settlement_refuses_malformed_payments(tmp_path: Path, payment: tuple, message: str) -> None:
    plan = [Payment(payer=payment[0], payee=payment[1], cents=payment[2])]
    with pytest.raises(ValueError, match=message):
        check_settlement(CheckInput(group=Group.REFUND, payments=plan), tmp_path)


def test_check_settlement_refuses_more_than_30_payments(tmp_path: Path) -> None:
    plan = [Payment(payer="Taj", payee="Rae", cents=1)] * 31
    with pytest.raises(ValueError, match="at most 30"):
        check_settlement(CheckInput(group=Group.REFUND, payments=plan), tmp_path)
