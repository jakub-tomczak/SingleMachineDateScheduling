import os
from options import *
import numpy as np
from methodRunner import invokeMethod
from IOmanager import getTest, dumpResults
from heuristics import tradeOffMethod

def main(): 
    arguments = { 
            'k' : 1,    #which test from test is going to be used
            'n' : 10,   #what is the instance size
            'h' : 0.6,
            'method' : tradeOffMethod
    }
    validateInput(arguments)
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

     
def validateInput(arguments):
    assert len(options.testsDirectory) > 0 and len(options.outputDirectory) > 0, 'Check tests or output directory (cannot be empty)'
    assert arguments['method'], 'Method to invoke cannot be empty.'
    assert arguments['k'] >= 0 and arguments['k'] < 10, 'There are only 10 tests for each instance available'
    
if __name__ == '__main__':
    main()