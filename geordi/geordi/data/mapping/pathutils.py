def make_callable(value):
    if not callable(value):
        return lambda *args, **kwargs: value
    else:
        return value

def no_op_value(value, *args, **kwargs):
    return value
