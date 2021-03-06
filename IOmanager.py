from __future__ import print_function
import os
from options import Instance, Result, Task


def read_test_file(instance_size, program_options):
    assert instance_size in program_options.instances_sizes, \
        'There is no test for an instance of a size {}.'.format(instance_size)
    fullpath = os.path.join(program_options.tests_directory, 'sch{}.txt'.format(instance_size))
    try:
        with open(fullpath, 'r') as instanceFile:
            number_of_tests = int(instanceFile.readline().strip())
            tests = list()
            for test in range(number_of_tests):
                number_of_lines_in_test = int(instanceFile.readline().strip())
                for lineIndex in range(number_of_lines_in_test):
                    tests.append(Task(instanceFile.readline().split(), lineIndex))
            return tests
    except FileNotFoundError:
        ExceptionPrinter.print_exception('File `{}` not found.'.format(fullpath))
        exit(1)


# n = instance size
# k = number of test
def get_test(instance, program_options):
    res = read_test_file(instance.n, program_options)
    if res is None or len(res) <= instance.k:
        exit(2)
    start_index = instance.n*instance.k
    return [res[x] for x in range(start_index, start_index+instance.n)]


def get_best_result(instance_to_find, best_results):
    temp = list(filter(lambda x: x[0] == instance_to_find, best_results))
    if len(temp) > 0:
        num = temp[0][1]
        is_optimal = num[-1] == '*'
        if is_optimal:
            return float(num[:-1]), is_optimal
        else:
            return float(num), is_optimal
    else:
        return 0


def get_best_results(program_options):
    if not program_options.compare_with_best_results:
        return None
    fullpath = os.path.join(program_options.tests_directory, program_options.best_results_filename)
    results = []
    h = [.2, .4, .6, .8]
    try:
        with open(fullpath, 'r') as instanceFile:
            for n in program_options.instances_sizes:
                # line with number n
                instanceFile.readline()
                for k in range(10):
                    line = instanceFile.readline().split()
                    [results.append((Instance(n, k, h[i]), line[i])) for i in range(4)]
            return results
    except FileNotFoundError:
        ExceptionPrinter.print_exception('File `{}` not found.'.format(fullpath))
        exit(1)


def dump_results(result, program_options, filename, comment=''):
    methods = {
        'out': dump_txt_result,
        'txt': dump_txt_result,
        'csv': dump_batch_results,
        'latex': dump_batch_results
    }
    if program_options.dump_format not in methods:
        ExceptionPrinter.print_exception('There is no method for this format: {}. Available types : {}'.format(program_options.dump_format,
                                                                                    ', '.join(methods.keys())))
    else:
        try:
            methods[program_options.dump_format](result, program_options, filename, comment)
        except:
            exit(2)

def dump_txt_result(result, options, filename, comment):
    if options.output_directory != '' and not os.path.exists(options.output_directory):
        os.mkdir(options.output_directory)
    path = os.path.join(options.output_directory,
                        '{}.{}'.format(filename, options.dump_format))
    data = "{}\n{}".format(int(result.cost), " ".join(map(str, result.order)))

    with open(path, 'w') as outFile:
        outFile.write(data)


def dump_batch_results(result, options, filename, comment):
    path = os.path.join(options.output_directory, '{}.{}'.format(filename, options.dump_format))
    with open(path, 'w') as outFile:
        if isinstance(result, list):
            [outFile.write(result_to_string(result[x], options.dump_format, num=x+1)) for x in range(len(result))]
        elif isinstance(result, Result):
            outFile.write(result_to_string(result, options.dump_format))


def result_to_string(result, file_format, num=0):
    assert file_format in ['csv', 'latex'], 'File format should be csv or latex. {} is not supported.'. \
        format(file_format)
    result.instance.k = result.instance.k + 1
    if file_format == 'csv':
        return '{};{};{};{};{};{};{}\n'.format(result.instance.n, result.instance.k, result.instance.h,
                                               result.instance.best_cost, result.cost,
                                               round(compare_with_best_cost(result), 2),
                                               result.time)
    else:
        return '{} & {} & {} & {} & {}{} & {} & {} & {} \\\ \hline\n'.format(num, result.instance.n, result.instance.k,
                                                                             result.instance.h,
                                                                             result.instance.best_cost,
                                                                             '*' if result.instance.best_cost_is_optimal else '',
                                                                             result.cost, round(compare_with_best_cost(result), 2), round(result.time, 4))


def get_out_filename_from_instance(instance):
    return '{}_{}_{}_{}'.format(instance.index, instance.n, instance.k + 1, int(instance.h * 10))


def compare_with_best_cost(result):
    if(result.instance.best_cost == 0):
        return 0
    return (result.cost - result.instance.best_cost) / result.instance.best_cost * 100


class GeneralPrint():
    @staticmethod
    def print_data(data):
        print(data)


class ExceptionPrinter:
    @staticmethod
    def print_exception(data):
        GeneralPrint.print_data('Exception: {}'.format(data))
        

class DebugPrinter:
    def __init__(self, instance, options):
        self.instance = instance
        self.options = options
        self.path = os.path.join(options.debug_directory,
                                 '{}_{}_{}_{}_{}.out'.format(options.debug_filename, instance.index, instance.n,
                                                             instance.k + 1, int(instance.h * 10)))
        if options.debug:
            import time
            self.log('\n------------\n{}'.format(time.asctime(time.localtime(time.time()))))
            if options.debug_directory != '' and not os.path.exists(options.debug_directory):
                os.mkdir(options.debug_directory)

    def dump_instance(self):
        self.log(self.instance)

    def log(self, data):
        if self.options.debug:
            data = '{}\n'.format(data)
            if self.options.verbose_debug:
                GeneralPrint.print_data(data)
            try:
                with open(self.path, 'a+') as outFile:
                    outFile.write(data)
            except Exception as e:
                GeneralPrint.print_data("Couldn't dump debug data to a file {}. Cause: {}".format(self.path, e))
