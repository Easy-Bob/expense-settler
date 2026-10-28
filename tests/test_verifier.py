from __future__ import annotations

import ast
from dataclasses import replace
from pathlib import Path

from slimconfig import build_output, plain_output

import verifier
from contract import TOOLS, BalancesInput, CheckInput, Group, Payment, ReadInput, SettleInput, Tool
from plugin import check_settlement, get_balances, read_expenses

# NanoAgent's sandbox lets a verifier import only these, contract and its own package.
ALLOWED_IMPORTS = {
    "__future__", "collections", "dataclasses", "decimal", "difflib", "enum", "fractions", "functools",
    "hashlib", "itertools", "json", "math", "operator", "pathlib", "re", "statistics", "string",
    "textwrap", "typing", "unicodedata",
}  # fmt: skip
FORBIDDEN_NAMES = {"__import__", "compile", "eval", "exec", "getattr", "globals", "open", "setattr", "vars"}


# The verifier gets contract instances, as NanoAgent's sandbox builds them from JSON.
def verify_input(tool: str, value: dict) -> dict:
    return verifier.verify_input(tool, build_output(value, TOOLS[Tool(tool)][0]))


def verify_output(tool: str, given: dict, made, workspace: Path) -> dict:
    given_class, made_class = TOOLS[Tool(tool)]
    return verifier.verify_output(
        tool, build_output(given, given_class), build_output(plain_output(made), made_class), str(workspace)
    )


def test_the_verifier_imports_only_what_the_sandbox_allows() -> None:
    for path in Path(verifier.__file__).parent.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                assert all(alias.name.split(".")[0] in ALLOWED_IMPORTS for alias in node.names), path.name
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                assert node.module.split(".")[0] in ALLOWED_IMPORTS | {"contract"}, path.name
            elif isinstance(node, ast.Name):
                assert node.id not in FORBIDDEN_NAMES, f"{path.name} uses {node.id}"


def test_checks_what_the_types_cannot_say() -> None:
    plan = {"group": "refund", "payments": [{"payer": "Taj", "payee": "Rae", "cents": 4000}]}
    assert verify_input("check_settlement", plan)["valid"] is True
    selfpay = {"group": "refund", "payments": [{"payer": "Rae", "payee": "Rae", "cents": 1}]}
    assert verify_input("check_settlement", selfpay)["valid"] is False
    nothing = {"group": "refund", "payments": [{"payer": "Taj", "payee": "Rae", "cents": 0}]}
    assert verify_input("check_settlement", nothing)["valid"] is False


def test_tool_outputs_are_checked(tmp_path: Path) -> None:
    given = {"group": "trip"}
    assert verify_output("read_expenses", given, read_expenses(ReadInput(group=Group.TRIP), tmp_path), tmp_path)[
        "valid"
    ]
    owed = get_balances(BalancesInput(group=Group.TRIP), tmp_path)
    assert verify_output("get_balances", given, owed, tmp_path)["valid"] is True
    owed.balances[0] = replace(owed.balances[0], cents=owed.balances[0].cents + 1)
    assert "add up to 0" in verify_output("get_balances", given, owed, tmp_path)["message"]
    plan = {"group": "refund", "payments": [{"payer": "Taj", "payee": "Rae", "cents": 4000}]}
    made = check_settlement(
        CheckInput(group=Group.REFUND, payments=[Payment(payer="Taj", payee="Rae", cents=4000)]), tmp_path
    )
    assert verify_output("check_settlement", plan, made, tmp_path)["valid"] is True
    made.settles = True
    assert verify_output("check_settlement", plan, made, tmp_path)["valid"] is False


def test_the_answer_key_is_checked_against_its_own_expenses(tmp_path: Path, pinned: dict) -> None:
    key = pinned[Group.CLUB]
    assert verify_output("pin_settlement", {"group": "club"}, key, tmp_path)["valid"] is True
    assert verify_output("pin_settlement", {"group": "trip"}, key, tmp_path)["valid"] is False
    assert verify_output("pin_settlement", {"group": "club"}, replace(key, minimum=6), tmp_path)["valid"] is False


def test_the_task_input_is_the_reference_tools() -> None:
    assert TOOLS[Tool.PIN_SETTLEMENT][0] is SettleInput
