import numpy as np
from options import options
def tradeOffMethod(arguments):
    #arguments to local vars
    instance = arguments['instance']
    h = arguments['h']
    tasksLength = sum([x[0] for x in instance]) #sum by index 0 = p
    dueDate = h*tasksLength
    
    #calculate penalties
    #for an earliness
    instance[:,4] = instance[:,0] / instance[:,1]
    #for a tardiness
    instance[:,5] = instance[:,0] / instance[:,2]
    
    earlinessArray = np.array(sorted(instance, key=lambda task: task[4], reverse=True)) #sort by the earliness coeff
    tardinessArray = np.array(sorted(instance, key=lambda task: task[5], reverse=True)) #sort by the tardiness coeff
    #print(earlinessArray)
    #print(tardinessArray)
    currentLength = 0
    currentCost = 0
    #iteration of the algorithm
    iter = 0

    #what task should we take in the current iteration?
    #earlinessIndex = 0
    #tardinessIndex = 0

    #check wheter the current best task is not exceeding dueDate limit (in both direction - depending on the stage)
    canAddAnotherTask = True
    #flag that indicates whether we've recalculated tardiness penalties and removed already assigned tasks (in the earliness stage)
    #if h>.5 we start from earliness stage so recalculating earlinessArray is not necessary
    recalculatedTardinessArray = h<.5
    recalculatedEarlinessArray = h>.5
    #indices of assigned tasks
    tasksAssigned = []
    #tardiness should be reversed
    tardinessAssigned = []
    earlinessStage = h>.5
    
    tardinessDueDate = tasksLength - dueDate
    currentTardinessLength = 0

    while(currentLength < tasksLength and iter < arguments['n']+1):
        if earlinessStage:
            if not recalculatedEarlinessArray:
                #take only not assigned elements
                earlinessArray = np.array([x for x in earlinessArray if x[3] not in tasksAssigned])
                if options.debug:
                    print('earliness: assigned {}, to assign {}'.format(tasksAssigned, earlinessArray[:,3]))
                recalculatedEarlinessArray = True 
            #print(iter, 'earliness stage')
            #prefer earliness - earliness stage
            #tasks that will fit before dueDate
            #x[4] - earliness penalty when adding this element in the current iteration
            #x[6]==1 task has been already assigned

            #take only not assigned tasks
            earlinessArray = np.array([x for x in earlinessArray if x[6]!=1 and 
                (h<0.5 or x[0]+currentLength <= dueDate) ]) #if h<.5 then earliness stage is the second one so we don't care about the limit 
            
            #found no candidates for the bestTask, continue in tardiness stage
            if len(earlinessArray) == 0:
                earlinessStage = False
                iter +=1
                continue
            bestTask = earlinessArray[0]
            
            #print(iter, ' > ',currentLength, bestTask, currentCost)
            #task used - assign its global id (to be found in tardinessArray)
            tasksAssigned.append(int(bestTask[3])) #[3] -> index
            #and mark it as used
            bestTask[6] = 1 #TODO rewrite it, in order not to use a number as a flag -> it's float!
            #prolong already assigned tasks length
            currentLength += bestTask[0]
            currentCost += (dueDate - currentLength)*bestTask[1]
            if options.debug:
                print('iter {} -> earliness: chosen task x:{},a:{}, length {}, dueDate {}, cost {}'.format(iter, bestTask[0], bestTask[1], currentLength, dueDate, currentCost))
        else:
            #print(iter, 'tardiness stage')
            #prefer tardiness - tardiness stage
            if not recalculatedTardinessArray:
                #take only not assigned elements
                tardinessArray = np.array([x for x in tardinessArray if x[3] not in tasksAssigned])
                # earliness may have ended up with currentLength lower than dueDate
                # recalculating is needed to add proper tardiness penalties
                # however, additional sorting is not necessary
                # so, from tardiness penalty substract the difference between
                # dueDate and currentLength 
                #tardinessArray[:, 5] = (dueDate - currentLength)*tardinessArray[:,2] #[:,2] -> tardiness coeff
                recalculatedTardinessArray = True 
                if options.debug:
                    print('tardiness: assigned {}, to assign {}'.format(tasksAssigned, tardinessArray[:,3]))
            
            tardinessArray = np.array([x for x in tardinessArray if x[6]!=1 and 
               ( h>0.5 or (tasksLength-dueDate)-currentLength-x[0] >=0) ]) #if h>0.5 then we don't care about the size - earliness stage was first
               #otherwise check if current task is not longer than the total time for tardiness stage
            
            #found no candidates for the bestTask, continue in earliness stage
            if len(tardinessArray) == 0:
                earlinessStage = True
                iter += 1
                continue
            
            bestTask = tardinessArray[0]
            
            #print(iter, ' > ',currentLength, bestTask, currentCost)
            #task used - assign its global id (to be found in tardinessArray)
            tardinessAssigned.append(int(bestTask[3])) #[3] -> index
            #and mark it as used
            bestTask[6] = 1 #TODO rewrite it, in order not to use a number as a flag -> it's float!
            #prolong already assigned tasks length
            currentLength += bestTask[0]
            addedCost = (tardinessDueDate-currentTardinessLength)*bestTask[2]
            currentTardinessLength += bestTask[0]
            currentCost += addedCost
            if options.debug:
                print('iter {} -> tardiness: chosen task x:{},b:{}, length {}, dueDate {}, cost {}, added:{}'.format(iter, bestTask[0], bestTask[2], currentLength, dueDate, currentCost, addedCost))

        iter += 1
    
    tardinessAssigned.reverse()
    tasksAssigned = tasksAssigned + tardinessAssigned
    if options.debug:
        print("assigned tasks {}".format(tasksAssigned))
    if arguments['n'] > 20:
        tasksAssigned = []
    if options.debug:
        print('ended on iteration {}, length {}, dueDate {}, cost {}'.format(iter, currentLength, dueDate, currentCost))

    resultCorrect = 1 if currentLength == tasksLength else 0
    return (iter, currentLength, dueDate, currentCost, tasksLength, tasksAssigned, resultCorrect)
