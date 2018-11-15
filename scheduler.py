import argparse
from method_runner import invoke_method
from IOmanager import get_test, dump_results, DebugPrinter, get_best_result, get_best_results, \
    get_out_filename_from_instance, compare_with_best_cost, GeneralPrint, ExceptionPrinter
from heuristics import second_method
from options import Instance, Options
from validator import validate_result
import numpy as np


def instance_runner(instance, program_options, debug_printer):
    instance.data = get_test(instance, program_options)
    method_to_invoke = program_options.method

    debug_printer.dump_instance()
    result = invoke_method(method_to_invoke, instance, debug_printer)

    if result is not None and program_options.print_result_to_stdout:
        GeneralPrint.print_data('Time is {:0.9f} the result (cost): {}'.format(result.time, result.cost))
        if program_options.dump_results:
            dump_results(result, program_options, '{}_{}'.format(program_options.txt_filename,
                                                                 get_out_filename_from_instance(result.instance)))
    else:
        GeneralPrint.print_data('Execution time is {:0.20f}'.format(result.time))

    validated_result = validate_result(instance, result.order)
    result.is_solution_feasible = validated_result.cost == result.cost
    if not result.is_solution_feasible:
        GeneralPrint.print_data("Result is not equal to validated result: {} != {}".format(result.cost, validated_result.cost))
    else:
        GeneralPrint.print_data("Feasible solution")
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
    program_options.method = second_method
    try:
        validate_input(args_instance, program_options)
    except AssertionError as e:
        ExceptionPrinter.print_exception(e)
        exit(2)

    printer = DebugPrinter(args_instance, program_options)
    if best_results is not None:
        args_instance.best_cost, args_instance.best_cost_is_optimal = get_best_result(args_instance, best_results)
    result = instance_runner(args_instance, program_options, printer)
    GeneralPrint.print_data('method: {}'.format(program_options.method.__name__))
    if result.is_solution_feasible and program_options.compare_with_best_results:
        GeneralPrint.print_data('cost: {}, optimal_cost {}{}, {}%'.
              format(result.cost, args_instance.best_cost,
                     '*' if args_instance.best_cost_is_optimal else '',
                     round(compare_with_best_cost(result), 2)))


def validate_input(instance, program_options):
    assert program_options.method, 'Method to invoke cannot be empty.'
    assert instance.k in range(10), 'k={} is not valid. Should be in range <1,10>.' \
                                    ' There are only 10 tests for each instance available'.format(instance.k + 1)
    assert instance.n in [10, 20, 50, 100, 200, 500, 1000], \
        'n={} is not valid. It must be a number from the set [10, 20, 50, 100, 200, 500, 1000]'.format(instance.n)
    assert 0 <= instance.h <= 1, 'h={} is not valid. h must be in range <0, 1>.'


def check_order_manually(instance):
    instance.data = get_test(instance, Options())
    order = [0, 3, 6, 8, 9, 5, 4, 1, 7, 2]
    result = validate_result(instance, order)
    GeneralPrint.print_data("instance n={}, k={}, h={}\nresult: {}\nlength {}".format(instance.n, instance.k, instance.h, result.cost,
                                                                    result.length))


def check_all_instances(program_options, best_results):
    miscalculated_instances = []
    results = []

    program_options.dump_results = False
    program_options.method = second_method
    program_options.debug = False
    program_options.batch_runner_filename = 'batch_{}_method'.format(program_options.method.__name__)
    program_options.dump_batch_runner = True
    program_options.dump_format = 'csv'

    for n in program_options.instances_sizes:
        for k in range(10): # [4, 9]
            for h in [.2, .4, .6, .8]:
                current_instance = Instance(n, k, h)
                printer = DebugPrinter(current_instance, program_options)
                GeneralPrint.print_data('n {} k {}, h {}'.format(n, k, h))
                if program_options.compare_with_best_results:
                    current_instance.best_cost, current_instance.best_cost_is_optimal = \
                        get_best_result(current_instance, best_results)

                result = instance_runner(current_instance, program_options, printer)
                results.append(result)
                if not result.is_solution_feasible:
                    miscalculated_instances.append('{} {} {}'.format(n, k, h))

    if len(miscalculated_instances) > 0:
        GeneralPrint.print_data('Miscalculated instances:')
        for row in miscalculated_instances:
            GeneralPrint.print_data(row)
    else:
        GeneralPrint.print_data('All instances calculated correctly')

    if program_options.dump_batch_runner:
        dump_results(results, program_options, program_options.batch_runner_filename)
    stats = list(map(lambda x: compare_with_best_cost(x), results))
    GeneralPrint.print_data('mean = {}\nmin = {}\nmax = {}'.format(np.mean(stats), min(stats), max(stats)))
