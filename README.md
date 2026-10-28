# Expense Settler

A `nanoagent.plugin/v0001` plugin. Its task, `settle`, gives an agent a
group's shared expenses (who paid, how much, and who shares each one). The
agent must find payments that leave everyone even with **the fewest possible
payments**. A rule-based verifier applies the payments, checks every balance
reaches exactly 0, and computes the true minimum itself.

## Tools

| Tool | Does | Code |
|---|---|---|
| `pin_settlement` | The answer key: the group's expenses, every member's balance and the fewest payments, pinned before the agent starts | `src/plugin/pin.py` |
| `read_expenses` | The group's members and expense log | `src/plugin/read.py` |
| `get_balances` | Every member's balance in cents: positive when the group owes them, negative when they owe it | `src/plugin/balances.py` |
| `check_settlement` | Whether a plan of payments brings every balance to exactly 0, and who is still off by how much. It never says whether the plan is the shortest | `src/plugin/check.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `settle` | Settles a group's expenses with the fewest payments | `agent`, with `read_expenses`, `get_balances` and `check_settlement`; reference `pin_settlement` |

## The task

Friends share costs: one pays the hotel, another dinner. Each member ends
with a balance, and the balances add up to 0. There are many ways to pay
everyone back. The fewest payments come from splitting the members into as
many groups as possible whose balances add up to exactly 0: a group of *k*
members needs only *k − 1* payments. The obvious plan (whoever owes most pays
whoever is owed most) often needs more. Finding the groups is the agent's job;
the tools do all the arithmetic.

### The money rules (`src/plugin/money.py`)

- All money is whole cents.
- Each sharer of an expense owes `floor(amount × weight / total weight)`; the
  cents left over go one each to the sharers in the order they are listed
  ($1.00 shared by A, B, C is 34, 33, 33). A refund (negative amount) is split
  the same way on its size, then negated.
- A balance is what a member paid minus what they owe.
- The fewest payments is the number of non-zero members minus the most groups
  they split into that each add up to 0, computed exactly by dynamic
  programming over subsets of members.

### The groups

The groups are bundled in `src/plugin/data/<group>.json`.
`src/plugin/tools_dev/build_groups.py` builds them from specs and refuses a
group whose fewest payments or greedy plan length differs from its spec. Some
expenses come in sets that cancel out, so the expense log does not give away
which balances cancel; only the balances do.

| Group | Members | Expenses | Fewest payments | Greedy plan | What it tests |
|---|---|---|---|---|---|
| `roommates` | 4 | 8 | 3 | 3 | Leftover cents ($10.00 shared three ways) |
| `dinner` | 3 | 4 | 2 | 2 | Someone pays for a meal they did not eat |
| `trip` | 6 | 12 | 4 | 5 | Uneven shares; a hidden pair beats the greedy plan |
| `club` | 10 | 17 | 7 | 9 | Three groups that cancel out among ten members |
| `settled` | 4 | 6 | 0 | 0 | Everyone is already even: the answer is no payments |
| `pennies` | 5 | 6 | 3 | 3 | 1 to 7 cent expenses, where the leftover-cent rule decides; one member ends at 0 |
| `refund` | 4 | 7 | 2 | 2 | Refunds (negative amounts) |

## The verifier

`verifier/task.py` runs four checks in order. It recomputes every balance and
the fewest payments from the pinned expenses itself, with its own copy of the
money rules, instead of trusting the key.

| # | Check | Fails when | Score |
|---|---|---|---|
| 1 | `key-integrity` | The key is altered (it no longer matches its sha256), is another group's, or its balances or minimum differ from what its expenses give | 0 |
| 2 | `submitted-shape` | Another group; a non-member; someone paying themselves; a payment under 1 cent; more than 30 payments | 0 |
| 3 | `settles` | After the payments a balance is not exactly 0 | 0 |
| 4 | `minimal` | It settles but with more payments than the minimum | minimum ÷ payments, at most 0.99 |

Valid, and score 1.0, only when all four hold. Any plan of the shortest length
passes: there is no single expected answer. The message names the failing
check, e.g. `settles: after the payments Rae is still owed $0.01 and Taj still
owes $0.01` or `minimal: 9 payments settle the group, but 7 are enough`.

## Layout

It has the standard plugin layout, which NanoAgent requires:

```text
.
├── nanoagent.yaml   # manifest (a slimconfig ManifestConfig): id, runtime, permissions, tools, tasks
├── contract.py      # each tool's and task's typed input and output: slimconfig Output classes
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env             # needed environment variable names (none here)
├── src/plugin/      # the MCP server (__main__.py, its IMPLEMENTATIONS table), the tools, money.py, data/ and tools_dev/
├── tests/           # money, minimum, group, tool and verifier tests, and tests/cases/: scripted submissions with their verdicts
├── ui/              # outputs drawn from their JSON Schema
├── product/         # the product page a catalog shows: product.yaml and icon.svg
└── verifier/        # deterministic verifier package, one module per tool, and task.py for settle
```

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

`uv run pytest` runs, without a model and without the network, the money
rules, the fewest-payments solver against a brute force on 200 random cases,
the groups, every tool, and `tests/cases/`: 24 scripted submissions, each with
the verdict it expects (shortest plans for every group, greedy plans, plans
that miss by a cent, malformed payments and an altered key). To rebuild the
groups, or check the bundled ones are what the generator builds:

```bash
uv run python -m plugin.tools_dev.build_groups --check
```
