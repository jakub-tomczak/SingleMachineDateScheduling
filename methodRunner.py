import time

def getTime():
    return time.time()

def invokeMethod(method, instance, programOptions):
    if method is not None:
        start = getTime()
        methodResult = method(instance, programOptions)
        stop = getTime()
        methodResult.time = stop - start
        return methodResult
        
    return None