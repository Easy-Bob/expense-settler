from .checks import result


def verify_input(value):
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    members = output_value.members
    if output_value.group is not input_value.group:
        return result(False, f"the expenses are for {output_value.group.value}, not {input_value.group.value}")
    if len(set(members)) != len(members):
        return result(False, "a member is listed twice")
    ids = [expense.id for expense in output_value.expenses]
    if len(set(ids)) != len(ids):
        return result(False, "an expense id is listed twice")
    for expense in output_value.expenses:
        if expense.paid_by not in members or not expense.shares:
            return result(False, f"{expense.id} is paid by a non-member or shared by no one")
        if any(share.member not in members or share.weight < 1 for share in expense.shares):
            return result(False, f"{expense.id} is shared with a non-member or a weight below 1")
    return result(True, "the expenses are well formed", expenses=len(ids))
