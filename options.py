class options:
    def __init__(self):
        self.method = None
        self.printResultToStdout = True
        self.testsDirectory = 'instances'
        self.outputDirectory = 'output'
        self.instancesSizes = [10,20,50,100,200,500,1000]
        self.dumpResults = True
        self.dumpFormat = "txt"
        self.debug = False

class instance:
    def __init__(self, n, k, h, index =''):
        self.n = n
        self.k = k
        self.h = h
        self.index = index
        self.data = None

class result:
    def __init__(self, instance):
        self.time = .0
        self.order = []
        self.length = 0
        self.cost = 0
        self.totalLength = 0
        self.dueDate = 0
        self.instance = instance