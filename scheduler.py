import argparse
from methodRunner import invokeMethod
from IOmanager import getTest, dumpResults, debugPrinter, getBestResult, getBestResults
from heuristics import tradeOffMethod, secondMethod
from options import instance, options
from validator import validate_result

def printInstance(instance):
    for i in range(len(instance)):
        print('x:{}, a:{}, b:{}, index:{}, earliness:{}, tardiness:{}'.format(
            instance[i,0], instance[i,1], instance[i,2], instance[i,3], instance[i,4], instance[i,5]
        ))
def instanceRunner(instance, programOptions, debugPrinter):
    instance.data = getTest(instance, programOptions)
    methodToInvoke = programOptions.method

    result = invokeMethod(methodToInvoke, instance, debugPrinter)

    if result != None and programOptions.printResultToStdout:
        print('Time is {:0.9f} the result (cost): {}'.format(result.time, result.cost))
        if programOptions.dumpResults:
            dumpResults(result, programOptions)
    else:
        print('Execution time is {:0.20f}'.format(result.time))

    validated_result = validate_result(instance, result.order)
    result.is_solution_feasible = validated_result.cost == result.cost
    if not result.is_solution_feasible:
        print("Result is not equal to validated result: {} != {}".format(result.cost, validated_result.cost))
    else:
        print("Feasible solution")
    return result

def parseArguments():
    parser = argparse.ArgumentParser(description='', add_help=False)
    parser.add_argument('n', type=int)
    parser.add_argument('k', type=int)
    parser.add_argument('h', type=float)
    args = parser.parse_args()
    #k loaded from file should be in range <0,9>
    return instance(n = args.n, k = args.k - 1, h = args.h)


def main(args_instance, best_results, program_options):
    program_options.method = tradeOffMethod
    printer = debugPrinter(args_instance, program_options)
    args_instance.best_cost, args_instance.best_cost_is_optimal = getBestResult(args_instance, best_results)
    try:
        validateInput(args_instance, program_options)
    except AssertionError as e:
        print(e)
        exit(2)
    result = instanceRunner(args_instance, program_options, printer)
    print('method: {}'.format(program_options.method.__name__))
    if result.is_solution_feasible:
        print('cost: {}, optimal_cost {}{}, {}%'.
              format(result.cost, args_instance.best_cost,
                     '*' if args_instance.best_cost_is_optimal else '',
                     round((result.cost-args_instance.best_cost)/result.cost*100,2)))

def validateInput(instance, programOptions):
    assert programOptions.method, 'Method to invoke cannot be empty.'
    assert instance.k in range(10), 'k={} is not valid. Should be in range <1,10>. There are only 10 tests for each instance available'.format(instance.k+1)
    assert instance.n in [10, 20, 50, 100, 200, 500, 1000], 'n={} is not valid. It must be a number from the set [10, 20, 50, 100, 200, 500, 1000]'.format(instance.n)
    assert 0 <= instance.h <= 1, 'h={} is not valid. h must be in range <0, 1>.'

def check_order_manually(instance):
    instance.data = getTest(instance, options())
    print(instance.data[0,:])
    order = [0, 3, 6, 8, 9, 5, 4, 1, 7, 2]
    result = validate_result(instance, order)
    print("instance n={}, k={}, h={}\nresult: {}\nlength {}".format(instance.n, instance.k, instance.h, result.cost, result.length))

def check_all_instances(program_options, best_results):
    miscalculated_instances = []
    results = []

    program_options.dumpResults = False
    program_options.method = tradeOffMethod
    program_options.debug = False
    program_options.batchRunnerFilename = 'batch_{}_method'.format(program_options.method.__name__)
    program_options.dumpBatchRunner = True
    program_options.dumpFormat = 'csv'

    for n in program_options.instancesSizes:
        for k in range(10):
            for h in [.2, .4, .6, .8]:
                current_instance = instance(n, k, h)
                printer = debugPrinter(current_instance, program_options)
                print('n {} k {}, h {}'.format(n, k, h))
                current_instance.best_cost, current_instance.best_cost_is_optimal =\
                    getBestResult(current_instance, best_results)

                result = instanceRunner(current_instance, program_options, printer)
                results.append(result)
                if not result.is_solution_feasible:
                    miscalculated_instances.append('{} {} {}'.format(n, k, h))

    if len(miscalculated_instances) > 0:
        print('Miscalculated instances:')
        for row in miscalculated_instances:
            print(row)
    else:
        print('All instances calculated correctly')

    if program_options.dumpBatchRunner:
        dumpResults(results, program_options)


if __name__ == '__main__':
    args_instance = parseArguments()
    program_options = options()
    best_results = getBestResults(program_options)
    #main(args_instance, best_results, program_options)
    check_all_instances(program_options, best_results)
    exit(0)
