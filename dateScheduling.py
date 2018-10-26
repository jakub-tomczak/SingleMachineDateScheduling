import os
import numpy as np
import argparse
from methodRunner import invokeMethod
from IOmanager import getTest, dumpResults
from heuristics import tradeOffMethod
from options import instance, options

def printInstance(instance):
    for i in range(len(instance)):
        print('x:{}, a:{}, b:{}, index:{}, earliness:{}, tardiness:{}'.format(
            instance[i,0], instance[i,1], instance[i,2], instance[i,3], instance[i,4], instance[i,5]
        ))
def instanceRunner(instance, programOptions):
    instance.data = getTest(instance, programOptions)
    methodToInvoke = programOptions.method

    result = invokeMethod(methodToInvoke, instance, programOptions)

    if result != None and programOptions.printResultToStdout:
        print('Time is {:0.9f} the result (cost): {}'.
            format(result.time, result.cost))
        if programOptions.dumpResults:
            dumpResults(instance, result, programOptions)
    else:
        print('Execution time is {:0.20f}'.format( result.time) )

def parseArguments():
    parser = argparse.ArgumentParser(description='', add_help=False)
    parser.add_argument('-n', type=int,
                        help='Number of tasks from set [10,20,50,100,200]')
    parser.add_argument('-k', type=int,
                        help='Instance index, natural number in range <1,10>')
    parser.add_argument('-h', type=float,
                        help='Used to calculate due date, real number in range <0,1>')
    parser.add_argument('-index', type=str, default=0,
                        help='Student\'s index')
    args = parser.parse_args()
    if args.n is None or args.k is None or args.h is None:
        print("Not all parameters have been specified.Args = {}".format(args))
        exit(2)
    #k loaded from file should be in range <0,9>
    return instance(n = args.n, k = args.k - 1, h = args.h, index=args.index )


def main(instance): 
    programOptions = options()
    programOptions.method = tradeOffMethod

    try:
        validateInput(instance, programOptions)
    except AssertionError as e:
        print(e)
        exit(2)
    instanceRunner(instance, programOptions)
    
def validateInput(instance, programOptions):
    assert programOptions.method, 'Method to invoke cannot be empty.'
    assert instance.k in range(10), 'k={} is not valid. Should be in range <1,10>. There are only 10 tests for each instance available'.format(instance.k+1)
    assert instance.n in [10,20,50, 100, 200, 500, 1000], 'n={} is not valid. It must be a number from the set [10, 20, 50, 100, 200, 500, 1000]'.format(instance.n)
    assert instance.h >= 0 and instance.h <=1, 'h={} is not valid. h must be in range <0, 1>.'
    
if __name__ == '__main__':
    instance = parseArguments()
    main(instance)
    exit(0)