"""Checks shared by the tool verifiers, and the money rules recomputed on contract instances.

The money rules mirror src/plugin/money.py, which the verifier may not import: the verifier
recomputes every balance and the fewest payments from the expenses itself rather than trusting them.
"""

import hashlib
import json

MAX_PAYMENTS = 30


def result(valid, message, *, score=None, **details):
    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def split(amount, shares):
    """What each sharer owes of ``amount``: [(member, cents)]. Leftover cents go one each, in order."""
    total = sum(share.weight for share in shares)
    size = abs(amount)
    owed = [size * share.weight // total for share in shares]
    for k in range(size - sum(owed)):
        owed[k] += 1
    sign = -1 if amount < 0 else 1
    return [(share.member, sign * cents) for share, cents in zip(shares, owed, strict=True)]


def balances(members, expenses):
    """Every member's balance from contract expenses: what they paid minus what they owe."""
    owed = dict.fromkeys(members, 0)
    for expense in expenses:
        owed[expense.paid_by] += expense.amount_cents
        for member, cents in split(expense.amount_cents, expense.shares):
            owed[member] -= cents
    return owed


def minimum(values):
    """The fewest payments that settle ``values``: the non-zero count minus the most groups they
    split into that each add up to 0 (see src/plugin/money.py)."""
    nonzero = [value for value in values if value]
    count = len(nonzero)
    sums = [0] * (1 << count)
    most = [0] * (1 << count)
    for mask in range(1, 1 << count):
        low = (mask & -mask).bit_length() - 1
        sums[mask] = sums[mask & (mask - 1)] + nonzero[low]
        best = max(most[mask & ~(1 << k)] for k in range(count) if mask >> k & 1)
        most[mask] = best + (sums[mask] == 0)
    return count - most[(1 << count) - 1]


def table_sha256(members, expenses, owed, fewest):
    """The digest pin_settlement gives its key, from contract expenses and a {member: cents} dict."""
    rows = {
        "members": list(members),
        "expenses": [[e.id, e.paid_by, e.amount_cents, [[s.member, s.weight] for s in e.shares]] for e in expenses],
        "balances": [[member, cents] for member, cents in owed.items()],
        "minimum": fewest,
    }
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest()


def dollars(cents):
    return f"${abs(cents) // 100}.{abs(cents) % 100:02d}"


def payments_problem(members, payments):
    """What makes a list of contract payments malformed, or None."""
    if len(payments) > MAX_PAYMENTS:
        return f"{len(payments)} payments; a plan has at most {MAX_PAYMENTS}"
    for number, payment in enumerate(payments, start=1):
        for member in (payment.payer, payment.payee):
            if member not in members:
                return f"payment {number} names {member!r}, who is not a member ({', '.join(members)})"
        if payment.payer == payment.payee:
            return f"payment {number}: {payment.payer} pays themselves"
        if payment.cents < 1:
            return f"payment {number} moves {payment.cents} cents; a payment moves 1 cent or more"
    return None
