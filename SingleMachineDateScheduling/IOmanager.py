import os
import numpy as np
from options import *

def readTestFile(instanceSize):
    assert instanceSize in options.instancesSizes, 'There is no test for an instance of a size %s' % instanceSize
    fullpath = os.path.join(options.testsDirectory, 'sch{}.txt'.format(instanceSize))
    
    try:
        with open(fullpath, 'r') as instanceFile:
            numberOfTests = int(instanceFile.readline().strip())
            tests = np.empty((numberOfTests, instanceSize, 3))
            for test in range(numberOfTests):
                numberOfLinesInTest = int(instanceFile.readline().strip())
                for line in range(numberOfLinesInTest):
                    tests[test][line] = instanceFile.readline().split()
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