import time
import os
from options import *

def getTime():
    return time.time()

def readTestFile(instanceSize):
    instanceSize = instanceSize[0]
    assert instanceSize in options.instancesSizes, 'There is no test for an instance of a size %s' % instanceSize
    fullpath = os.path.join(options.testsDirectory, 'sch{}.txt'.format(instanceSize))
    
    try:
        with open(fullpath, 'r') as instanceFile:
            tests = []
            numberOfTests = int(instanceFile.readline().strip())
            for test in range(numberOfTests):
                tests.append([]) #another test from a file
                numberOfLinesInTest = int(instanceFile.readline().strip())
                for _ in range(numberOfLinesInTest):
                    [p, a, b] = instanceFile.readline().split()
                    tests[test].append( { 'p' : int(p), 'a' : int(a), 'b' : int(b)} )
            return tests
    except FileNotFoundError:
        print('File `{}` not found.'.format(fullpath))
        exit(0)

def dumpResults(name, result):
    fullpath = os.path.join(options.outputDirectory, 'out.txt')
    with open(fullpath, 'a') as outFile:
        outFile.write('{};{}\n'.format(
            name, result
        ))

def invokeMethod(method, arguments):
    result = {
        'time' : 0,
        'returnedValue' : None
    }

    if method is not None:
        start = getTime()
        returnedValue = method(arguments)
        stop = getTime()
        result['time'] = stop - start
        result['returnedValue'] = returnedValue
        
    return result

def main():
    arguments = { 
            'k' : 1,
            'n' : 10,
            'h' : 0.6 
    }
    arguments = [100]
    methodToInvoke = readTestFile

    validateInput(methodToInvoke, arguments)    
    result = invokeMethod(methodToInvoke, arguments)

    if result['returnedValue'] != None and options.printResultToStdout:
        print('Time is {:0.9f} the result: {}'.
            format(result['time'], result['returnedValue']))
    else:
        print('Execution time is {0:0.9f}'.format( result['time']) )

     
def validateInput(methodToInvoke, arguments):
    assert len(options.testsDirectory) > 0 and len(options.outputDirectory) > 0, 'Check tests or output directory (cannot be empty)' 
    assert methodToInvoke, 'Method to invoke cannot be empty.' 
    
if __name__ == '__main__':
    main()