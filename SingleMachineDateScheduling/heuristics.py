def tradeOffMethod(arguments):
    #arguments to local vars
    instance = arguments['instance']
    h = arguments['h']

    tasksLength = sum([x[0] for x in instance]) #sum by index 0 = p
    earlinessArray = sorted(instance, key=lambda task: task[1]) #sort by a
    tardinessArray = sorted(instance, key=lambda task: task[2], reverse=True) #sort by b

    d = h*tasksLength 
    currentLength = 0
    currentCost = 0

    tardinessIndex = 0
    earlinessIndex = 0

    while(currentLength < tasksLength):
        if h < .5 and currentLength < d:
            #prefer earliness
            pass
        else:
            #prefer tardiness

    return 0