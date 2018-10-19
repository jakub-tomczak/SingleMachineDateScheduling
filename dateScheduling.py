import os
from options import *
import numpy as np
import argparse
from methodRunner import invokeMethod
from IOmanager import getTest, dumpResults
from heuristics import tradeOffMethod

def printInstance(instance):
    for i in range(len(instance)):
        print('x:{}, a:{}, b:{}, index:{}, earliness:{}, tardiness:{}'.format(
            instance[i,0], instance[i,1], instance[i,2], instance[i,3], instance[i,4], instance[i,5]
        ))
def instanceRunner(arguments):
    arguments['instance'] = getTest(n = arguments['n'], k = arguments['k'])
    methodToInvoke = arguments['method']

    result = invokeMethod(methodToInvoke, arguments)

    if result['returnedValue'] != None and options.printResultToStdout:
        print('Time is {:0.9f} the result: {}'.
            format(result['time'], result['returnedValue']))
        if options.dumpResults:
            dumpResults(arguments, result)
    else:
        print('Execution time is {:0.20f}'.format( result['time']) )

def parseArguments():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('n', type=int,
                        help='Number of tasks from set [10,20,50,100,200]')
    parser.add_argument('k', type=int,
                        help='Instance index, natural number in range <1,10>')
    parser.add_argument('h', type=float,
                        help='Used to calculate due date, real number in range <0,1>')
    parser.add_argument('index', type=int, default=0,
                        help='Student\'s index')
    args = parser.parse_args()

    arguments = {
        'n' : args.n,
        'k' : args.k,
        'h' : args.h,
        'studentsIndex' : args.index
    }
    return arguments


def main(arguments): 
    arguments['method'] = tradeOffMethod
    validateInput(arguments)
    instanceRunner(arguments)
    #for k in range(10):
    #    arguments['k'] = k
    #    for h in [0.6, .8]:
    #        arguments['h'] = h
    #        instanceRunner(arguments)
     
def validateInput(arguments):
    assert arguments['method'], 'Method to invoke cannot be empty.'
    assert arguments['k'] > 0 and arguments['k'] <= 10, 'k={} is not valid. There are only 10 tests for each instance available'.format(arguments['k'])
    assert arguments['n'] in [10,20,50, 100, 200, 500, 1000], 'n={} is not valid. It must be a number from the set [10, 20, 50, 100, 200, 500, 1000]'.format(arguments['n'])
    assert arguments['h'] >= 0 and arguments['h'] <=1, 'h={} is not valid. h must be in range <0, 1>.'
    
if __name__ == '__main__':
    arguments = parseArguments()
    main(arguments)