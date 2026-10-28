"""The settle task's check: the payments bring every balance to exactly 0, with as few payments as can.

Four checks, in order. When the key is altered or the payments are malformed, nothing after is
judged. Payments that do not settle score 0. Payments that settle but are more than the minimum
score minimum / payments, at most 0.99. Valid only when all four hold.
"""

from .checks import balances, dollars, minimum, payments_problem, result, table_sha256

CHECKS = ["key-integrity", "submitted-shape", "settles", "minimal"]


def verdict(check, why, score=0.0, **details):
    return result(False, f"{check}: {why}", score=score, failed=check, **details)


def key_problem(arguments, reference):
    if reference is None:
        return "no answer key was pinned"
    if reference.group is not arguments.group:
        return f"the answer key is for {reference.group.value}, not {arguments.group.value}"
    pinned = {balance.member: balance.cents for balance in reference.balances}
    if reference.table_sha256 != table_sha256(reference.members, reference.expenses, pinned, reference.minimum):
        return "the answer key was altered: it no longer matches its sha256"
    owed = balances(reference.members, reference.expenses)
    if owed != pinned:
        return "the answer key's balances are not what its expenses give"
    if minimum(list(owed.values())) != reference.minimum:
        return "the answer key's minimum is not the fewest payments its balances need"
    return None


def off(left):
    """Who is still off after the payments, e.g. 'Ben is still owed $0.01 and Cara still owes $0.01'."""
    named = [
        f"{member} is still owed {dollars(cents)}" if cents > 0 else f"{member} still owes {dollars(cents)}"
        for member, cents in left.items()
        if cents
    ]
    if len(named) > 3:
        named = [*named[:3], f"{len(named) - 3} more are off"]
    return named[0] if len(named) == 1 else ", ".join(named[:-1]) + " and " + named[-1]


def verify_task(arguments, output, reference, workspace):
    """``output``: a contract SettleOutput; ``reference``: pin_settlement's PinOutput."""
    problem = key_problem(arguments, reference)
    if problem:
        return verdict("key-integrity", problem)
    if output.group is not arguments.group:
        return verdict("submitted-shape", f"the payments are for {output.group.value}, not {arguments.group.value}")
    problem = payments_problem(reference.members, output.payments)
    if problem:
        return verdict("submitted-shape", problem)

    owed = balances(reference.members, reference.expenses)
    left = dict(owed)
    for payment in output.payments:
        left[payment.payer] += payment.cents
        left[payment.payee] -= payment.cents
    count, fewest = len(output.payments), reference.minimum
    details = {"payments": count, "minimum": fewest}
    if any(left.values()):
        return verdict("settles", f"after the payments {off(left)}", **details)
    if count > fewest:
        return verdict(
            "minimal",
            f"{count} payments settle the group, but {fewest} are enough",
            score=min(0.99, fewest / count),
            **details,
        )
    return result(
        True, f"All {len(CHECKS)} checks hold: {count} payments settle the group, the fewest possible.", **details
    )
