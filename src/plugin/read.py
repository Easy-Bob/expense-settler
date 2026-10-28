"""read_expenses: a group's members and expense log, as bundled."""

from __future__ import annotations

from pathlib import Path

from contract import ExpensesOutput, ReadInput
from plugin.groups import expense_outputs, load_group


def read_expenses(value: ReadInput, workspace: Path) -> ExpensesOutput:
    data = load_group(value.group)
    return ExpensesOutput(group=value.group, members=data["members"], expenses=expense_outputs(data))
