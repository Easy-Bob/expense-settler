"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    PIN_SETTLEMENT = "pin_settlement"
    READ_EXPENSES = "read_expenses"
    GET_BALANCES = "get_balances"
    CHECK_SETTLEMENT = "check_settlement"


class Task(Enum):
    SETTLE = "settle"


class Group(Enum):
    ROOMMATES = "roommates"
    DINNER = "dinner"
    TRIP = "trip"
    CLUB = "club"
    SETTLED = "settled"
    PENNIES = "pennies"
    REFUND = "refund"


GROUP = "The bundled group whose expenses are settled"
MEMBER = "A member's name, spelled as read_expenses and get_balances give it"
CENTS = "An amount in whole cents, e.g. 1250 for $12.50"
BALANCE = "The member's balance in cents: positive when the group owes them, negative when they owe the group"


@dataclass
class Share(Output):
    member: Annotated[str, MEMBER]
    weight: Annotated[int, "How many shares of the expense the member takes, 1 or more"]


@dataclass
class Expense(Output):
    id: Annotated[str, "The expense's id, e.g. e3"]
    description: Annotated[str, "What the expense was for"]
    paid_by: Annotated[str, "The member who paid it"]
    amount_cents: Annotated[int, "What was paid, in cents; negative for a refund"]
    shares: Annotated[list[Share], "Who shares the cost and how many shares each takes, in order"]


@dataclass
class Balance(Output):
    member: Annotated[str, MEMBER]
    cents: Annotated[int, BALANCE]


@dataclass
class Payment(Output):
    payer: Annotated[str, "The member who pays: one who owes"]
    payee: Annotated[str, "The member who is paid: one who is owed"]
    cents: Annotated[int, "How much, in whole cents, more than 0"]


@dataclass
class SettleInput(Output):
    group: Annotated[Group, GROUP]


@dataclass
class PinOutput(Output):
    group: Annotated[Group, GROUP]
    members: Annotated[list[str], "Every member, in order"]
    expenses: Annotated[list[Expense], "Every expense, in order"]
    balances: Annotated[list[Balance], "Every member's balance, in member order"]
    minimum: Annotated[int, "The fewest payments that settle the group"]
    table_sha256: Annotated[
        str, "The sha256 of the members, expenses, balances and minimum, as checks.table_sha256 computes it"
    ]


@dataclass
class ReadInput(Output):
    group: Annotated[Group, GROUP]


@dataclass
class ExpensesOutput(Output):
    group: Annotated[Group, GROUP]
    members: Annotated[list[str], "Every member, in order"]
    expenses: Annotated[list[Expense], "Every expense, in order"]


@dataclass
class BalancesInput(Output):
    group: Annotated[Group, GROUP]


@dataclass
class BalancesOutput(Output):
    group: Annotated[Group, GROUP]
    balances: Annotated[list[Balance], "Every member's balance, in member order; they add up to 0"]


@dataclass
class CheckInput(Output):
    group: Annotated[Group, GROUP]
    payments: Annotated[list[Payment], "The planned payments, 0 to 30 of them"]


@dataclass
class CheckOutput(Output):
    settles: Annotated[bool, "Whether the payments bring every balance to exactly 0"]
    payments: Annotated[int, "How many payments the plan has"]
    remaining: Annotated[
        list[Balance], "Each member still off after the payments, with what they are still owed (+) or owe (-)"
    ]


@dataclass
class SettleOutput(Output):
    group: Annotated[Group, GROUP]
    payments: Annotated[list[Payment], "The payments that settle the group, as few as possible"]


TOOLS = {
    Tool.PIN_SETTLEMENT: (SettleInput, PinOutput),
    Tool.READ_EXPENSES: (ReadInput, ExpensesOutput),
    Tool.GET_BALANCES: (BalancesInput, BalancesOutput),
    Tool.CHECK_SETTLEMENT: (CheckInput, CheckOutput),
}

TASKS = {Task.SETTLE: (SettleInput, SettleOutput)}
