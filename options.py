class options:
    def __init__(self):
        self.method = None
        self.printResultToStdout = True
        self.testsDirectory = 'instances'
        self.outputDirectory = ''
        self.debugDirectory = 'out_debug'
        self.instancesSizes = [10,20,50,100,200,500,1000]
        self.dumpResults = False
        self.dumpFormat = "txt"
        self.txtFilename = "dupa"
        self.debugFilename = "DEBUG_second"
        self.debug = True #dump debug to a file
        self.verboseDebug = False #print text during debug
        self.bestResultsFilename = "best_results.txt"
        self.dumpBatchRunner = False
        self.batchRunnerFilename = "batch"

class instance:
    index = '127083'

    def __init__(self, n, k, h):
        self.n = n
        self.k = k
        self.h = h
        self.data = None
        self.best_cost = 0
        self.best_cost_is_optimal = False

    def __eq__(self, other):
        if isinstance(other, instance):
            return self.n == other.n and self.k == other.k and self.h == other.h
        return False

class result:
    def __init__(self, instance):
        self.time = .0
        self.order = []
        self.length = 0
        self.cost = 0
        self.totalLength = 0
        self.dueDate = 0
        self.instance = instance
        self.is_solution_feasible = False
