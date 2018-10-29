class Options:
    def __init__(self):
        self.method = None
        self.print_result_to_stdout = True
        self.tests_directory = 'instances'
        self.output_directory = ''
        self.debug_directory = 'out_debug'
        self.instances_sizes = [10, 20, 50, 100, 200, 500, 1000]
        self.dump_results = False
        self.dump_format = "txt"
        self.txt_filename = "text_file"
        self.debug_filename = "DEBUG_second"
        self.debug = False  # dump debug to a file
        self.verbose_debug = False  # print text during debug
        self.compare_with_best_results = False
        self.best_results_filename = "best_results.txt"
        self.dump_batch_runner = False
        self.batch_runner_filename = "batch"


class Instance:
    index = '127083'

    def __init__(self, n, k, h):
        self.n = n
        self.k = k
        self.h = h
        self.data = None
        self.best_cost = 0
        self.best_cost_is_optimal = False

    def __eq__(self, other):
        if isinstance(other, Instance):
            return self.n == other.n and self.k == other.k and self.h == other.h
        return False


class Result:
    def __init__(self, instance):
        self.time = .0
        self.order = []
        self.length = 0
        self.cost = 0
        self.totalLength = 0
        self.dueDate = 0
        self.instance = instance
        self.is_solution_feasible = False
