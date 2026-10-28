"""The bundled groups: each group's members and expense log, as src/plugin/data/<group>.json holds them."""

from __future__ import annotations

import json
from pathlib import Path

from contract import Expense, Group, Share

DATA = Path(__file__).parent / "data"


def load_group(group: Group) -> dict:
    """``{"group", "members", "expenses": [{"id", "description", "paid_by", "amount_cents", "shares"}]}``."""
    return json.loads((DATA / f"{group.value}.json").read_text())


def expense_outputs(data: dict) -> list[Expense]:
    return [
        Expense(
            id=expense["id"],
            description=expense["description"],
            paid_by=expense["paid_by"],
            amount_cents=expense["amount_cents"],
            shares=[Share(member=share["member"], weight=share["weight"]) for share in expense["shares"]],
        )
        for expense in data["expenses"]
    ]
