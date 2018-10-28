import os
import json
import numpy as np
from options import instance

def readTestFile(instanceSize, programOptions):
    assert instanceSize in programOptions.instancesSizes, 'There is no test for an instance of a size %s' % instanceSize
    fullpath = os.path.join(programOptions.testsDirectory, 'sch{}.txt'.format(instanceSize))
    try:
        with open(fullpath, 'r') as instanceFile:
            numberOfTests = int(instanceFile.readline().strip())
            #4th element for an index, 5th for an earliness penalty, 6th for a tardiness penalty, 7th 0-task not used, 1-task used
            tests = np.empty((numberOfTests, instanceSize, 7)) 
            for test in range(numberOfTests):
                numberOfLinesInTest = int(instanceFile.readline().strip())
                for lineIndex in range(numberOfLinesInTest):
                    tests[test][lineIndex][:3] = instanceFile.readline().split() #set first 3 elements
                    tests[test][lineIndex][3] = lineIndex
            return tests
    except FileNotFoundError:
        print('File `{}` not found.'.format(fullpath))
        exit(1)

#n = instance size
#k = number of test
def getTest(instance, programOptions):
    res = readTestFile(instance.n, programOptions)
    if res is None or len(res) <= instance.k:
        exit(2) 
    return res[instance.k]


def getBestResult(instance_to_find, best_results):
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


def getBestResults(programOptions):
    fullpath = os.path.join(programOptions.testsDirectory, programOptions.bestResultsFilename)
    results = []
    h = [.2, .4, .6, .8]
    try:
        with open(fullpath, 'r') as instanceFile:
            for n in programOptions.instancesSizes:
                # line with number n
                instanceFile.readline()
                for k in range(10):
                    line = instanceFile.readline().split()
                    [results.append((instance(n, k, h[i]), line[i])) for i in range(4)]
            return results
    except FileNotFoundError:
        print('File `{}` not found.'.format(fullpath))
        exit(1)

def dumpResults(result, programOptions, comment = ''):
    methods = {
        'json' : dumpJSONResult,
        'txt' : dumpTXTResult,
        'csv' : dumpBatchResults,
        'latex' : dumpLatexTable
    }
    if programOptions.dumpFormat not in methods:
        print('There is no method for this format: {}. Available types : {}'.format(programOptions.dumpFormat, methods.keys))
    else:
        try:
            methods[programOptions.dumpFormat](result, programOptions, comment)
        except:
            exit(2)

def dumpJSONResult(result, options, comment):
    path = os.path.join(options.outputDirectory, 'out.json')
    data = []
    if os.path.exists(path):
        with open(path, 'r') as inFile:
            inFile.seek(0,2) #go the end
            size = inFile.tell()
            inFile.seek(0,0) #return to the beginning
            if size > 0:
                try:
                    data = json.load(inFile)
                except json.decoder.JSONDecodeError:
                    pass #content may be not a valid json content
    data.append({ 
        'time' : result.time,
        'cost' : result.cost,
        'length' : result.length,
        'dueDate': result.dueDate,
        'h' : result.instance.h,
        'k' : result.instance.k,
        'n' : result.instance.n,
        'comment' : result.instance.index,
        'assignmentOrder' : result.order
    })
    
    with open(path, 'w') as outFile:
        json.dump(data, outFile, indent=1)

def dumpTXTResult(result, options, comment):
    path = os.path.join(options.outputDirectory, '{}_{}_{}_{}_{}.out'.format(options.txtFilename, result.instance.index, result.instance.n, result.instance.k+1, int(result.instance.h*10))) #arguments['k']+1 => pwdk in out file should be in range <1, 10>
    data = "{}\n{}".format(int(result.cost), " ".join(map(str, result.order)) )

    with open(path, 'w') as outFile:
        outFile.write(data)


def dumpBatchResults(result, options, comment):
    path = os.path.join(options.outputDirectory, '{}.csv'.format(options.batchRunnerFilename))
    with open(path, 'w') as outFile:
        [outFile.write(resultToString(x, 'csv')) for x in result]


def dumpLatexTable(result, options, comment):
    path = os.path.join(options.outputDirectory, '{}.latex'.format(options.batchRunnerFilename))

    with open(path, 'w') as outFile:
        [outFile.write(resultToString(result[x], 'latex', x+1)) for x in range(len(result))]


def resultToString(result, file_format, num = 0):
    assert file_format in ['csv', 'latex'], 'File format should be csv or latex. {} is not supported.'.\
        format(file_format)
    result.instance.k = result.instance.k+1
    if file_format == 'csv':
        return '{};{};{};{};{};{};{}\n'.format(result.instance.n, result.instance.k, result.instance.h,
                                             result.instance.best_cost, result.cost,
                                             round((result.cost - result.instance.best_cost)/result.cost * 100, 2),
                                             result.time)
    else:
        return '{} & {} & {} & {} & {}{} & {} & {} & {} \\\ \hline\n'.format(num, result.instance.n, result.instance.k,
            result.instance.h, result.instance.best_cost, '*' if result.instance.best_cost_is_optimal else '',
            result.cost, round((result.cost - result.instance.best_cost) / result.cost * 100, 2), round(result.time, 4))

class debugPrinter:
    def __init__(self, instance, options):
        self.instance = instance
        self.options = options
        self.path = os.path.join(options.debugDirectory, 'DEBUG_{}_{}_{}_{}.out'.format(instance.index, instance.n, instance.k+1, int(instance.h*10))) 
        if options.debug:
            import time
            self.print('\n------------\n{}'.format( time.asctime(time.localtime(time.time())) ))

    def print(self, data):
        if self.options.debug:
            data = '{}\n'.format(data)
            if self.options.verboseDebug:
                print(data)
            try:
                with open(self.path, 'a+') as outFile:
                    outFile.write(data)
            except Exception as e:
                print("Couldn't dump debug data to a file {}. Cause: {}".format(self.path, e))
