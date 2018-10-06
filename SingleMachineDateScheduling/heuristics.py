import numpy as np
def tradeOffMethod(arguments):
    #arguments to local vars
    instance = arguments['instance']
    h = arguments['h']
    tasksLength = sum([x[0] for x in instance]) #sum by index 0 = p
    dueDate = int(h*tasksLength) 
    
    #calculate penalties
    #for an earliness
    instance[:,4] = (dueDate - instance[:,0])*instance[:,1]
    #for a tardiness
    dueDateToEnd = tasksLength - dueDate
    instance[:,5] = dueDateToEnd*instance[:,2]
    
    earlinessArray = np.array(sorted(instance, key=lambda task: task[4])) #sort by the earliness penalties
    tardinessArray = np.array(sorted(instance, key=lambda task: task[5])) #sort the tardiness penalties
    print(earlinessArray)
    print(tardinessArray)
    currentLength = 0
    currentCost = 0
    #iteration of the algorithm
    iter = 0

    #what task should we take in the current iteration?
    earlinessIndex = 0
    tardinessIndex = 0

    #check wheter the current best task is not exceeding dueDate limit (in both direction - depending on the stage)
    canAddAnotherTask = True
    #flag that indicates whether we've recalculated tardiness penalties and removed already assigned tasks (in the earliness stage)
    recalculatedTardinessArray = False
    #indices of assigned tasks
    tasksAssigned = []
    
    while(currentLength < tasksLength and iter < 15):
        if h > .5 and currentLength < dueDate and canAddAnotherTask:
            print(iter, 'earliness stage')
            #prefer earliness - earliness stage
            #tasks that will fit before dueDate
            #x[4] - earliness penalty when adding this element in the current iteration
            #x[6]==1 task has been already assigned
            bestTask = earlinessArray[earlinessIndex]
            
            if bestTask[4] < 0:
                canAddAnotherTask = False
                continue
            
            print(iter, ' > ',currentLength, bestTask, currentCost)
            earlinessIndex+=1
            #task used - assign its global id (to be found in tardinessArray)
            tasksAssigned.append(int(bestTask[3])) #[3] -> index
            #and mark it as used
            bestTask[6] = 1 #TODO rewrite it, in order not to use a number as a flag -> it's float!
            #prolong already assigned tasks length
            currentLength += bestTask[0]
            currentCost += bestTask[4]
            earlinessArray[:,4] -= bestTask[0]*earlinessArray[:,1]
        else:
            print(iter, 'tardiness stage')
            #prefer tardiness - tardiness stage
            if not recalculatedTardinessArray:
                #take only not assigned elements
                tardinessArray = [x for x in tardinessArray if x[6]!=1] 
                # earliness may have ended up with currentLength lower than dueDate
                # recalculating is needed to add proper tardiness penalties
                # however, additional sorting is not necessary
                # so, from tardiness penalty substract the difference between
                # dueDate and currentLength 
                tardinessArray[:, 5] = (dueDate - currentLength)*tardinessArray[:,2] #[:,2] -> tardiness coeff
                recalculatedTardinessArray = True 
            
            bestTask = tardinessArray[tardinessIndex]
            
            #check wheter the current best task is not exceeding dueDate limit 
            if bestTask[4] < 0:
                canAddAnotherTask = False
                #TODO check whether algorithm has been already in the earliness stage
                continue #may enter earliness stage in the next iteration, so don't break
            
            print(iter, ' > ',currentLength, bestTask, currentCost)
            tardinessIndex+=1
            #task used - assign its global id (to be found in tardinessArray)
            tasksAssigned.append(int(bestTask[3])) #[3] -> index
            #prolong used tasks length
            currentLength += bestTask[0]
            currentCost += bestTask[5]

            tardinessArray[:,5] -= bestTask[0]*earlinessArray[:,1]

        iter += 1
    print('ended on iteration {}, length {}, dueDate {}, cost {}'.format(iter, currentLength, dueDate, currentCost))
    return 0
