import time


def get_time():
    return time.time()


def invoke_method(method, instance, program_options):
    if method is not None:
        start = get_time()
        method_result = method(instance, program_options)
        stop = get_time()
        method_result.time = stop - start
        return method_result
    return None
