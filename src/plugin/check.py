"""check_settlement: whether a plan of payments brings every balance to exactly 0, and who is still off.
It never says whether the plan is the shortest: finding that is the agent's job."""

from __future__ import annotations

from pathlib import Path

from contract import Balance, CheckInput, CheckOutput
from plugin.groups import load_group
from plugin.money import MAX_PAYMENTS, apply, balances


def check_payments(members: list[str], payments) -> None:
    """Raise unless every payment is between two different members of the group and moves 1 cent or more."""
    if len(payments) > MAX_PAYMENTS:
        raise ValueError(f"a plan has at most {MAX_PAYMENTS} payments, not {len(payments)}")
    for number, payment in enumerate(payments, start=1):
        for member in (payment.payer, payment.payee):
            if member not in members:
                raise ValueError(f"payment {number}: {member!r} is not a member of the group ({', '.join(members)})")
        if payment.payer == payment.payee:
            raise ValueError(f"payment {number}: {payment.payer} cannot pay themselves")
        if payment.cents < 1:
            raise ValueError(f"payment {number}: a payment moves 1 cent or more, not {payment.cents}")


def check_settlement(value: CheckInput, workspace: Path) -> CheckOutput:
    data = load_group(value.group)
    check_payments(data["members"], value.payments)
    owed = balances(data["members"], data["expenses"])
    left = apply(owed, [(p.payer, p.payee, p.cents) for p in value.payments])
    remaining = [Balance(member=member, cents=cents) for member, cents in left.items() if cents]
    return CheckOutput(settles=not remaining, payments=len(value.payments), remaining=remaining)
