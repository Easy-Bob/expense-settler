from .checks import MAX_PAYMENTS, result


def verify_input(value):
    payments = value.payments
    if len(payments) > MAX_PAYMENTS:
        return result(False, f"a plan has at most {MAX_PAYMENTS} payments")
    for number, payment in enumerate(payments, start=1):
        if payment.payer == payment.payee:
            return result(False, f"payment {number}: {payment.payer} pays themselves")
        if payment.cents < 1:
            return result(False, f"payment {number} moves less than 1 cent")
    return result(True, "input is valid")


def verify_output(input_value, output_value, workspace):
    if output_value.payments != len(input_value.payments):
        return result(False, f"the plan has {len(input_value.payments)} payments, not {output_value.payments}")
    if any(balance.cents == 0 for balance in output_value.remaining):
        return result(False, "remaining lists a member who is even")
    if output_value.settles == bool(output_value.remaining):
        return result(False, "settles must be true exactly when no one remains off")
    return result(True, "the check is consistent", settles=output_value.settles)
