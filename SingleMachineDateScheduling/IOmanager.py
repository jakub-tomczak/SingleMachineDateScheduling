import os
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

def dumpResults(name, result):
    fullpath = os.path.join(options.outputDirectory, 'out.txt')
    with open(fullpath, 'a') as outFile:
        outFile.write('{};{}\n'.format(
            name, result
        ))