"""get_balances: every member's balance in cents, by the money rules (positive: the group owes them)."""

from __future__ import annotations

from pathlib import Path

from contract import Balance, BalancesInput, BalancesOutput
from plugin.groups import load_group
from plugin.money import balances


def get_balances(value: BalancesInput, workspace: Path) -> BalancesOutput:
    data = load_group(value.group)
    owed = balances(data["members"], data["expenses"])
    return BalancesOutput(
        group=value.group, balances=[Balance(member=member, cents=cents) for member, cents in owed.items()]
    )
