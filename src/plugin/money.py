"""The money rules, on plain values: shares, balances, payments, and the fewest payments that settle.

All money is whole cents. An expense's sharers each owe floor(amount x weight / total weight); the
cents left over go one each to the sharers in the order they are listed. A refund (a negative
amount) is split the same way on its size, then negated. A balance is what a member paid minus
what they owe: positive when the group owes them.
"""

from __future__ import annotations

MAX_PAYMENTS = 30


def split(amount: int, shares: list[tuple[str, int]]) -> list[tuple[str, int]]:
    """What each sharer owes of ``amount``: [(member, cents)], in the order the shares are listed."""
    total = sum(weight for _, weight in shares)
    size = abs(amount)
    owed = [size * weight // total for _, weight in shares]
    for k in range(size - sum(owed)):
        owed[k] += 1
    sign = -1 if amount < 0 else 1
    return [(member, sign * cents) for (member, _), cents in zip(shares, owed, strict=True)]


def balances(members: list[str], expenses: list[dict]) -> dict[str, int]:
    """Every member's balance, in member order, from expenses as the bundled data holds them."""
    result = dict.fromkeys(members, 0)
    for expense in expenses:
        result[expense["paid_by"]] += expense["amount_cents"]
        shares = [(share["member"], share["weight"]) for share in expense["shares"]]
        for member, cents in split(expense["amount_cents"], shares):
            result[member] -= cents
    return result


def apply(start: dict[str, int], payments: list[tuple[str, str, int]]) -> dict[str, int]:
    """The balances after ``payments`` [(payer, payee, cents)]: a payer's goes up, a payee's down."""
    result = dict(start)
    for payer, payee, cents in payments:
        result[payer] += cents
        result[payee] -= cents
    return result


def minimum(values: list[int]) -> int:
    """The fewest payments that settle ``values`` (which add up to 0).

    With n non-zero balances split into the most groups that each add up to 0, a group of k needs
    k - 1 payments, so the minimum is n minus that number of groups. most[mask] is the most such
    groups the members in ``mask`` can be split into: drop any one member from a mask whose sum is 0
    and it loses one group at most.
    """
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


def greedy(start: dict[str, int]) -> list[tuple[str, str, int]]:
    """The obvious plan: the member who owes most pays the member owed most, until all are even.
    Ties go to the name first in alphabetical order. Often more payments than the minimum."""
    left = dict(start)
    plan = []
    while any(left.values()):
        payer = min(left, key=lambda member: (left[member], member))
        payee = max(left, key=lambda member: (left[member], [-ord(c) for c in member]))
        cents = min(-left[payer], left[payee])
        plan.append((payer, payee, cents))
        left[payer] += cents
        left[payee] -= cents
    return plan


def shortest(start: dict[str, int]) -> list[tuple[str, str, int]]:
    """A plan with the fewest payments: split the members into the most groups that each add up to
    0, then settle each group greedily, which takes one payment fewer than its size."""
    members = [member for member in start if start[member]]
    count = len(members)
    sums = [0] * (1 << count)
    for mask in range(1, 1 << count):
        low = (mask & -mask).bit_length() - 1
        sums[mask] = sums[mask & (mask - 1)] + start[members[low]]
    most, pick = [0] * (1 << count), [0] * (1 << count)
    for mask in range(1, 1 << count):
        low = mask & -mask
        best = -1
        # Every group that holds the lowest member of ``mask`` and adds up to 0.
        sub = mask
        while sub:
            if sub & low and sums[sub] == 0 and most[mask ^ sub] + 1 > best:
                best, pick[mask] = most[mask ^ sub] + 1, sub
            sub = (sub - 1) & mask
        most[mask] = best
    plan, mask = [], (1 << count) - 1
    while mask:
        group = pick[mask]
        plan += greedy({members[k]: start[members[k]] for k in range(count) if group >> k & 1})
        mask ^= group
    return plan
