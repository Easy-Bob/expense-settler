"""Write the bundled groups, src/plugin/data/<group>.json, from the specs below.

Each group is a small expense log. Some expenses come in sets that cancel out (Ana pays a coffee
for Ana and Cara, Cara pays one back), so the log does not give away which members' balances
cancel; only the balances do. Before writing a group it computes the balances, the fewest payments
and the greedy plan's length, and refuses to write one that differs from its spec.

    uv run python -m plugin.tools_dev.build_groups          # rebuild every group
    uv run python -m plugin.tools_dev.build_groups --check  # rebuild in memory, compare with the files
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass

from contract import Group
from plugin.groups import DATA
from plugin.money import balances, greedy, minimum


@dataclass
class Spec:
    group: Group
    members: list[str]
    expenses: list[tuple]  # (description, paid_by, amount_cents, [member or (member, weight)])
    minimum: int
    greedy: int


def build(spec: Spec) -> dict:
    expenses = []
    for number, (description, paid_by, amount, sharers) in enumerate(spec.expenses, start=1):
        shares = [
            {"member": s, "weight": 1} if isinstance(s, str) else {"member": s[0], "weight": s[1]} for s in sharers
        ]
        expenses.append(
            {
                "id": f"e{number}",
                "description": description,
                "paid_by": paid_by,
                "amount_cents": amount,
                "shares": shares,
            }
        )
    return {"group": spec.group.value, "members": spec.members, "expenses": expenses}


def serialize(data: dict) -> str:
    return json.dumps(data, indent=1, sort_keys=True) + "\n"


def check(spec: Spec, data: dict) -> None:
    owed = balances(data["members"], data["expenses"])
    fewest, obvious = minimum(list(owed.values())), len(greedy(owed))
    if (fewest, obvious) != (spec.minimum, spec.greedy):
        raise SystemExit(
            f"{spec.group.value}: minimum {fewest} and greedy {obvious}, not {spec.minimum} and {spec.greedy}"
        )


SPECS = [
    Spec(
        Group.ROOMMATES,
        ["Ana", "Ben", "Cara", "Dan"],
        [
            ("Groceries", "Ana", 8743, ["Ana", "Ben", "Cara", "Dan"]),
            ("Internet bill", "Ben", 6000, ["Ana", "Ben", "Cara", "Dan"]),
            ("Cleaning supplies", "Cara", 1000, ["Ana", "Ben", "Cara"]),
            ("Pizza night", "Dan", 4599, ["Ana", "Ben", "Cara", "Dan"]),
            ("Electricity", "Ana", 11237, ["Ana", "Ben", "Cara", "Dan"]),
            ("Toilet paper", "Ben", 1999, ["Ben", "Cara", "Dan"]),
            ("Movie rental", "Cara", 599, ["Ana", "Cara", "Dan"]),
            ("Coffee beans", "Dan", 2350, ["Ana", "Dan"]),
        ],
        minimum=3,
        greedy=3,
    ),
    Spec(
        Group.DINNER,
        ["Eva", "Finn", "Gus"],
        [
            ("Dinner: Eva treats Finn and Gus", "Eva", 6400, ["Finn", "Gus"]),
            ("Drinks", "Finn", 2700, ["Eva", "Finn", "Gus"]),
            ("Dessert", "Gus", 1500, ["Eva", "Gus"]),
            ("Taxi home", "Finn", 1850, ["Finn", "Gus"]),
        ],
        minimum=2,
        greedy=2,
    ),
    Spec(
        Group.TRIP,
        ["Ana", "Ben", "Cara", "Dan", "Eli", "Fay"],
        [
            ("Hotel room for two", "Ana", 10000, ["Ana", "Ben"]),
            ("Boat tour", "Eli", 9000, ["Ana", "Eli", "Cara"]),
            ("Group dinner", "Cara", 8000, ["Cara", "Dan", "Eli", "Fay"]),
            ("Concert tickets (Dan brought a friend)", "Ben", 9000, ["Ben", ("Dan", 2)]),
            ("Car rental", "Ana", 6000, ["Ana", "Eli"]),
            ("Museum tickets for Eli and Fay", "Dan", 4000, ["Eli", "Fay"]),
            ("Breakfast", "Fay", 2400, ["Fay", "Ana", "Dan"]),
            ("Late-night groceries (Ben ate double)", "Dan", 9000, ["Dan", ("Ben", 2)]),
            ("Fuel", "Cara", 6000, ["Cara", "Eli"]),
            ("Parking", "Ana", 1600, ["Ana", "Fay"]),
            ("Snacks for Eli", "Fay", 500, ["Eli"]),
            ("Beach chairs", "Dan", 1600, ["Dan", "Fay"]),
        ],
        minimum=4,
        greedy=5,
    ),
    Spec(
        Group.CLUB,
        ["Kai", "Lea", "Max", "Nia", "Oto", "Pia", "Quin", "Rex", "Sam", "Tia"],
        [
            ("Tournament entry for Kai and Lea", "Kai", 7000, ["Kai", "Lea"]),
            ("Equipment", "Pia", 4000, ["Pia", "Quin"]),
            ("Team dinner", "Max", 6000, ["Max", "Nia", "Oto"]),
            ("Team photos", "Lea", 3000, ["Lea", "Sam", "Tia"]),
            ("Jerseys (Kai ordered two)", "Max", 6000, ["Max", ("Kai", 2)]),
            ("Court booking", "Pia", 7500, ["Pia", "Rex", "Sam"]),
            ("Trophy engraving", "Nia", 1500, ["Nia", "Oto", "Rex"]),
            ("Field rental", "Quin", 4000, ["Pia", "Quin"]),
            ("Bus tickets for Rex and Tia", "Quin", 2000, ["Rex", "Tia"]),
            ("Snacks", "Sam", 2000, ["Sam", "Lea"]),
            ("Referee fees (Max covered two games)", "Kai", 6000, ["Kai", ("Max", 2)]),
            ("Nia's water bottle", "Oto", 500, ["Nia"]),
            ("Pia's tape", "Rex", 500, ["Pia"]),
            ("Water", "Tia", 2000, ["Tia", "Lea"]),
            ("Tia's wristband", "Sam", 300, ["Tia"]),
            ("Oto's share of the engraving, paid back", "Oto", 500, ["Nia"]),
            ("Rex's share of the engraving, paid back", "Rex", 500, ["Nia"]),
        ],
        minimum=7,
        greedy=9,
    ),
    Spec(
        Group.SETTLED,
        ["Hal", "Ida", "Jon", "Kim"],
        [
            ("Week 1 groceries", "Hal", 4000, ["Hal", "Ida", "Jon", "Kim"]),
            ("Week 2 groceries", "Ida", 4000, ["Hal", "Ida", "Jon", "Kim"]),
            ("Pizza", "Hal", 2000, ["Hal", "Ida"]),
            ("Week 3 groceries", "Jon", 4000, ["Hal", "Ida", "Jon", "Kim"]),
            ("Wings", "Ida", 2000, ["Hal", "Ida"]),
            ("Week 4 groceries", "Kim", 4000, ["Hal", "Ida", "Jon", "Kim"]),
        ],
        minimum=0,
        greedy=0,
    ),
    Spec(
        Group.PENNIES,
        ["Lou", "Mia", "Ned", "Ola", "Pam"],
        [
            ("Gum", "Lou", 1, ["Mia", "Ned", "Ola"]),
            ("Stamp", "Mia", 5, ["Lou", "Mia", "Ned"]),
            ("Candy", "Ned", 4, ["Ola", "Pam", "Lou"]),
            ("Sticker", "Ola", 3, ["Pam", "Ola"]),
            ("Mint", "Pam", 2, ["Lou", "Mia", "Ned"]),
            ("Button", "Lou", 7, [("Ned", 2), "Mia"]),
        ],
        minimum=3,
        greedy=3,
    ),
    Spec(
        Group.REFUND,
        ["Rae", "Sol", "Taj", "Uma"],
        [
            ("Concert tickets", "Rae", 16000, ["Rae", "Sol", "Taj", "Uma"]),
            ("Refund: one show was cancelled", "Rae", -8000, ["Rae", "Sol", "Taj", "Uma"]),
            ("Taxi", "Sol", 3000, ["Sol", "Taj"]),
            ("Dinner", "Uma", 6000, ["Rae", "Sol", "Taj", "Uma"]),
            ("Partial refund on dinner", "Uma", -2000, ["Rae", "Sol", "Taj", "Uma"]),
            ("Parking", "Taj", 1000, ["Taj", "Sol"]),
            ("Coffee", "Uma", 2000, ["Rae", "Uma"]),
        ],
        minimum=2,
        greedy=2,
    ),
]


def main() -> None:
    stale = []
    for spec in SPECS:
        data = build(spec)
        check(spec, data)
        path = DATA / f"{spec.group.value}.json"
        if "--check" in sys.argv[1:]:
            if not path.exists() or path.read_text() != serialize(data):
                stale.append(path.name)
        else:
            path.write_text(serialize(data))
        print(f"{spec.group.value}: {len(spec.members)} members, minimum {spec.minimum}, greedy {spec.greedy}")
    if stale:
        raise SystemExit(f"stale groups: {', '.join(stale)}; rebuild them")


if __name__ == "__main__":
    main()
