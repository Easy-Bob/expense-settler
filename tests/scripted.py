"""A scripted settle run: the case's submission judged by the real verifier against the real key.

No model runs. A case (tests/cases/<name>.json) gives the group, the payments submitted as
[payer, payee, cents], optionally another group named in the submission or a tamper applied to the
key, and the verdict it expects.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from slimconfig import build_output, plain_output

import verifier
from contract import Group, Payment, SettleInput, SettleOutput

CASES = Path(__file__).parent / "cases"


def run_case(case: dict, workspace: Path, pinned: dict) -> dict:
    group = Group(case["group"])
    output = SettleOutput(
        group=Group(case.get("submit_group", group.value)),
        payments=[Payment(payer=payer, payee=payee, cents=cents) for payer, payee, cents in case["payments"]],
    )
    reference = pinned[group]
    if case.get("tamper") == "altered-key":
        balances = list(reference.balances)
        balances[0] = replace(balances[0], cents=balances[0].cents + 100)
        balances[1] = replace(balances[1], cents=balances[1].cents - 100)
        reference = replace(reference, balances=balances)
    elif case.get("tamper"):
        raise ValueError(f"unknown tamper {case['tamper']!r}")
    # The verifier gets contract instances, as NanoAgent's sandbox builds them from JSON.
    return verifier.verify_task(
        "settle",
        build_output({"group": group.value}, SettleInput),
        build_output(plain_output(output), SettleOutput),
        reference,
        str(workspace),
    )


def load_cases() -> list[dict]:
    return [json.loads(path.read_text()) | {"name": path.stem} for path in sorted(CASES.glob("*.json"))]
