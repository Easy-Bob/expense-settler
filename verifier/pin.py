from .checks import balances, minimum, result, table_sha256


def verify_input(value):
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    if output_value.group is not input_value.group:
        return result(False, f"the key is for {output_value.group.value}, not {input_value.group.value}")
    pinned = {balance.member: balance.cents for balance in output_value.balances}
    owed = balances(output_value.members, output_value.expenses)
    if owed != pinned:
        return result(False, "the pinned balances are not what the pinned expenses give")
    if minimum(list(owed.values())) != output_value.minimum:
        return result(False, "the pinned minimum is not the fewest payments the balances need")
    if output_value.table_sha256 != table_sha256(
        output_value.members, output_value.expenses, owed, output_value.minimum
    ):
        return result(False, "table_sha256 does not match the key")
    return result(True, "the key is consistent", minimum=output_value.minimum)
