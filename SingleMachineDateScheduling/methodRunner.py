import time

def getTime():
    return time.time()

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