from .checks import result


def verify_input(value):
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    members = [balance.member for balance in output_value.balances]
    if output_value.group is not input_value.group:
        return result(False, f"the balances are for {output_value.group.value}, not {input_value.group.value}")
    if len(set(members)) != len(members):
        return result(False, "a member is listed twice")
    if sum(balance.cents for balance in output_value.balances):
        return result(False, "the balances do not add up to 0")
    return result(True, "the balances add up to 0", members=len(members))
