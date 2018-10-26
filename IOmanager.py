import os
import json
import numpy as np

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

def dumpResults(arguments, result, programOptions, comment = ''):
    methods = {
        'json' : dumpJSONResult,
        'txt' : dumpTXTResult
    }
    if programOptions.dumpFormat not in methods:
        print('There is no method for this format: {}. Available types : {}'.format(programOptions.dumpFormat, methods.keys))
    else:
        try:
            methods[programOptions.dumpFormat](arguments, result, programOptions, comment)
        except:
            exit(2)

def dumpJSONResult(arguments, result, options, comment):
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
        'comment' : arguments['studentsIndex'],
        'assignmentOrder' : result.order
    })
    
    with open(path, 'w') as outFile:
        json.dump(data, outFile, indent=1)

def dumpTXTResult(arguments, result, options, comment):
    path = os.path.join(options.outputDirectory, 'sch_{}_{}_{}_{}.out'.format(result.instance.index, result.instance.n, result.instance.k+1, int(result.instance.h*10))) #arguments['k']+1 => pwdk in out file should be in range <1, 10>
    data = "{}\n{}".format(int(result.cost), " ".join(map(str, result.order)) )

    with open(path, 'w') as outFile:
        outFile.write(data)