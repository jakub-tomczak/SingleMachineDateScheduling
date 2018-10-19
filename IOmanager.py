import os
import json
import numpy as np
from options import *

def readTestFile(instanceSize):
    assert instanceSize in options.instancesSizes, 'There is no test for an instance of a size %s' % instanceSize
    fullpath = os.path.join(options.testsDirectory, 'sch{}.txt'.format(instanceSize))
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
        exit(0)

#n = instance size
#k = number of test
def getTest(n, k):
    return readTestFile(n)[k]

def dumpResults(arguments, result, format, comment = ''):
    methods = {
        'json' : dumpJSONResult,
        'txt' : dumpTXTResult
    }
    if format not in methods:
        print('There is no method for this format: {}. Available types : {}'.format(format, methods.keys))
    else:
        methods[format](arguments, result, comment)

def dumpJSONResult(arguments, result, comment):
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
        'time' : result['time'],
        'cost' : result['returnedValue'][3],
        'length' : result['returnedValue'][1],
        'dueDate': result['returnedValue'][2],
        'tasksLength' : result['returnedValue'][4],
        'h' : arguments['h'],
        'k' : arguments['k'],
        'n' : arguments['n'],
        'iterations': result['returnedValue'][0],
        'comment' : arguments['studentsIndex'],
        'assignmentOrder' : result['returnedValue'][5],
        'resultCorrect' : result['returnedValue'][6]
    })
    
    with open(path, 'w') as outFile:
        json.dump(data, outFile, indent=1)

def dumpTXTResult(arguments, result, comment):
    path = os.path.join(options.outputDirectory, 'sch_{}_{}_{}_{}.out'.format(arguments['studentsIndex'], arguments['n'], arguments['k'], int(arguments['h']*10)))
    data = "{}\n{}".format(result['returnedValue'][3], " ".join(map(str, result['returnedValue'][5])) )
    
    with open(path, 'w') as outFile:
        outFile.write(data)