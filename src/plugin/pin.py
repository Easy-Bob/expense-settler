"""pin_settlement, the settle task's reference: the group's expenses, balances and fewest payments,
out of the agent's sight. The verifier recomputes the balances and the minimum from the pinned
expenses itself, so the key only has to be the bundled group, unaltered."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from contract import Balance, PinOutput, SettleInput
from plugin.groups import expense_outputs, load_group
from plugin.money import balances, minimum


def table_sha256(members: list[str], expenses: list[dict], owed: dict[str, int], fewest: int) -> str:
    """The same digest verifier/checks.py computes, so the verifier can tell an altered key."""
    rows = {
        "members": members,
        "expenses": [
            [e["id"], e["paid_by"], e["amount_cents"], [[s["member"], s["weight"]] for s in e["shares"]]]
            for e in expenses
        ],
        "balances": [[member, cents] for member, cents in owed.items()],
        "minimum": fewest,
    }
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def pin_settlement(value: SettleInput, workspace: Path) -> PinOutput:
    data = load_group(value.group)
    owed = balances(data["members"], data["expenses"])
    fewest = minimum(list(owed.values()))
    return PinOutput(
        group=value.group,
        members=data["members"],
        expenses=expense_outputs(data),
        balances=[Balance(member=member, cents=cents) for member, cents in owed.items()],
        minimum=fewest,
        table_sha256=table_sha256(data["members"], data["expenses"], owed, fewest),
    )
