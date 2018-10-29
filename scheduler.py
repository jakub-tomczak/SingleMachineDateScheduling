import argparse
from method_runner import invoke_method
from IOmanager import get_test, dump_results, DebugPrinter, get_best_result, get_best_results
from heuristics import trade_off_method, second_method
from options import Instance, Options
from validator import validate_result


def print_instance(instance):
    for i in range(len(instance)):
        print('x:{}, a:{}, b:{}, index:{}, earliness:{}, tardiness:{}'.format(
            instance[i, 0], instance[i, 1], instance[i, 2], instance[i, 3], instance[i, 4], instance[i, 5]
        ))


def instance_runner(instance, program_options, debug_printer):
    instance.data = get_test(instance, program_options)
    method_to_invoke = program_options.method

    result = invoke_method(method_to_invoke, instance, debug_printer)

    if result is not None and program_options.print_result_to_stdout:
        print('Time is {:0.9f} the result (cost): {}'.format(result.time, result.cost))
        if program_options.dump_results:
            dump_results(result, program_options)
    else:
        print('Execution time is {:0.20f}'.format(result.time))

    validated_result = validate_result(instance, result.order)
    result.is_solution_feasible = validated_result.cost == result.cost
    if not result.is_solution_feasible:
        print("Result is not equal to validated result: {} != {}".format(result.cost, validated_result.cost))
    else:
        print("Feasible solution")
    return result


def parse_arguments():
    parser = argparse.ArgumentParser(description='', add_help=False)
    parser.add_argument('n', type=int)
    parser.add_argument('k', type=int)
    parser.add_argument('h', type=float)
    args = parser.parse_args()
    # k loaded from file should be in range <0,9>
    return Instance(n=args.n, k=args.k - 1, h=args.h)


def check_one_instance(args_instance, best_results, program_options):
    program_options.method = trade_off_method
    printer = DebugPrinter(args_instance, program_options)
    if best_results is not None:
        args_instance.best_cost, args_instance.best_cost_is_optimal = get_best_result(args_instance, best_results)
    try:
        validate_input(args_instance, program_options)
    except AssertionError as e:
        print(e)
        exit(2)
    result = instance_runner(args_instance, program_options, printer)
    print('method: {}'.format(program_options.method.__name__))
    if result.is_solution_feasible and program_options.compare_with_best_results:
        print('cost: {}, optimal_cost {}{}, {}%'.
              format(result.cost, args_instance.best_cost,
                     '*' if args_instance.best_cost_is_optimal else '',
                     round((result.cost - args_instance.best_cost) / result.cost * 100, 2)))


def validate_input(instance, program_options):
    assert program_options.method, 'Method to invoke cannot be empty.'
    assert instance.k in range(10), 'k={} is not valid. Should be in range <1,10>.' \
                                    ' There are only 10 tests for each instance available'.format(instance.k + 1)
    assert instance.n in [10, 20, 50, 100, 200, 500, 1000], \
        'n={} is not valid. It must be a number from the set [10, 20, 50, 100, 200, 500, 1000]'.format(instance.n)
    assert 0 <= instance.h <= 1, 'h={} is not valid. h must be in range <0, 1>.'


def check_order_manually(instance):
    instance.data = get_test(instance, Options())
    print(instance.data[0, :])
    order = [0, 3, 6, 8, 9, 5, 4, 1, 7, 2]
    result = validate_result(instance, order)
    print("instance n={}, k={}, h={}\nresult: {}\nlength {}".format(instance.n, instance.k, instance.h, result.cost,
                                                                    result.length))


def check_all_instances(program_options, best_results):
    miscalculated_instances = []
    results = []

    program_options.dump_results = False
    program_options.method = trade_off_method
    program_options.debug = False
    program_options.batch_runner_filename = 'batch_{}_method'.format(program_options.method.__name__)
    program_options.dump_batch_runner = True
    program_options.dump_format = 'csv'

    for n in program_options.instances_sizes:
        for k in range(10): # [4, 9]
            for h in [.2, .4, .6, .8]:
                current_instance = Instance(n, k, h)
                printer = DebugPrinter(current_instance, program_options)
                print('n {} k {}, h {}'.format(n, k, h))
                if program_options.compare_with_best_results:
                    current_instance.best_cost, current_instance.best_cost_is_optimal = \
                        get_best_result(current_instance, best_results)

                result = instance_runner(current_instance, program_options, printer)
                results.append(result)
                if not result.is_solution_feasible:
                    miscalculated_instances.append('{} {} {}'.format(n, k, h))

    if len(miscalculated_instances) > 0:
        print('Miscalculated instances:')
        for row in miscalculated_instances:
            print(row)
    else:
        print('All instances calculated correctly')

    if program_options.dump_batch_runner:
        dump_results(results, program_options)
