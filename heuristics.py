import numpy as np
from options import result
def tradeOffMethod(instance, options):
    methodResult = result(instance)
    #arguments to local vars
    tasksLength = sum([x[0] for x in instance.data]) #sum by index 0 => task's length
    methodResult.dueDate = int(instance.h*tasksLength)
    
    #calculate length/penalty ratios
    #for an earliness
    instance.data[:, 4] = instance.data[:,0] / instance.data[:,1]
    #for a tardiness
    instance.data[:, 5] = instance.data[:,0] / instance.data[:,2]
    
    earlinessArray = np.array(sorted(instance.data, key=lambda task: task[4], reverse=True)) #sort by the earliness ratio
    tardinessArray = np.array(sorted(instance.data, key=lambda task: task[5], reverse=True)) #sort by the tardiness ratio
    
    #iteration of the algorithm
    iter = 0
    
    #flag that indicates whether we've recalculated tardiness penalties and removed already assigned tasks (in the earliness stage)
    #if h>.5 we start from earliness stage so recalculating earlinessArray is not necessary
    recalculatedTardinessArray = instance.h<.5
    recalculatedEarlinessArray = instance.h>.5
    
    #indices of assigned tasks
    tasksAssigned = []
    #tardiness should be reversed
    tardinessAssigned = []
    
    #do we start from the earliness stage?
    earlinessStage = instance.h>.5
    
    tardinessDueDate = tasksLength - methodResult.dueDate
    currentTardinessLength = 0

    while(methodResult.length < tasksLength and iter < instance.n+1):
        if earlinessStage:
            if not recalculatedEarlinessArray:
                #take only not assigned elements
                earlinessArray = np.array([x for x in earlinessArray if x[3] not in tardinessAssigned])
                if options.debug:
                    print('earliness: assigned {}, to assign {}'.format(tasksAssigned, earlinessArray[:,3]))
                recalculatedEarlinessArray = True 
            #x[4] - task's length to earliness penalty ratio
            #x[6]==1 task has been already assigned

            #take only not assigned tasks
            earlinessArray = np.array([x for x in earlinessArray if x[6]!=1 and 
                (instance.h<0.5 or x[0]+methodResult.length <= methodResult.dueDate) ]) #if h<.5 then earliness stage is the second one so we don't care about the limit 
            
            #found no candidates for the bestTask, continue in tardiness stage
            if len(earlinessArray) == 0:
                earlinessStage = False
                iter +=1
                continue

            bestTask = earlinessArray[0]
            #add task to the list
            tasksAssigned.append(int(bestTask[3])) #[3] -> task's index
            #and mark it as used
            bestTask[6] = 1 #TODO rewrite it, in order not to use a number as a flag -> it's float!
            methodResult.length += bestTask[0]

            #put cost to add to another variable for debug purposes
            if methodResult.length < methodResult.dueDate:
                #earliness stage was first
                lengthToDueDate = methodResult.dueDate - methodResult.length
            else:
                lengthToDueDate = methodResult.dueDate - (methodResult.length - currentTardinessLength)
            costToAdd = lengthToDueDate*bestTask[1]
            methodResult.cost += costToAdd 
            if options.debug:
                print('adding {}*{}'.format(lengthToDueDate, bestTask[1]))
                print('iter {} -> earliness: chosen task id={}, x:{},a:{}, length {}, dueDate {}, cost {}, added:{}'.
                    format(iter, bestTask[3], bestTask[0], bestTask[1], methodResult.length, methodResult.dueDate, methodResult.cost, costToAdd))
        else:
            #tardiness stage
            if not recalculatedTardinessArray:
                #take only not assigned elements
                tardinessArray = np.array([x for x in tardinessArray if x[3] not in tasksAssigned])
                recalculatedTardinessArray = True 
                if options.debug:
                    print('tardiness: assigned {}, to assign {}'.format(tasksAssigned, tardinessArray[:,3]))
            
            tardinessArray = np.array([x for x in tardinessArray if x[6]!=1 and 
               ( instance.h>0.5 or (tasksLength-methodResult.dueDate)-methodResult.length >=0) ]) #if h>0.5 then we don't care about the size - earliness stage was first
               #otherwise check if current task is not longer than the total time for tardiness stage
            
            #found no candidates for the bestTask, continue in earliness stage
            if len(tardinessArray) == 0:
                #TODO check if earliness stage has been performed already in order to finish
                earlinessStage = True
                iter += 1
                continue
            
            bestTask = tardinessArray[0]
            tardinessAssigned.append(int(bestTask[3])) #[3] -> index
            bestTask[6] = 1 #TODO rewrite it, in order not to use a number as a flag -> it's float!
            
            #for the first task currentTardinessLength - we count the penalty based on the termination time
            if methodResult.length < methodResult.dueDate and currentTardinessLength == 0 and iter > 1:
                lengthToDueDate = tasksLength - (methodResult.length + bestTask[0]) - (methodResult.dueDate - methodResult.length)
            else:
                #tardiness phase was first
                lengthToDueDate = tardinessDueDate - currentTardinessLength

            methodResult.length += bestTask[0]            
            currentTardinessLength += bestTask[0]
            costToAdd = lengthToDueDate*bestTask[2]
            methodResult.cost += costToAdd
            if options.debug:
                print("adding {}*{}".format(lengthToDueDate, bestTask[2]))
                print('iter {} -> tardiness: chosen task id={}, x:{},b:{}, length {}, dueDate {}, cost {}, added:{}'
                    .format(iter, bestTask[3], bestTask[0], bestTask[2], methodResult.length, methodResult.dueDate, methodResult.cost, costToAdd))

        iter += 1
    
    tardinessAssigned.reverse()
    methodResult.order = tasksAssigned + tardinessAssigned
    if options.debug:
        print("assigned tasks {}".format(tasksAssigned))
    #if arguments['n'] > 20:
    #    tasksAssigned = []
    if options.debug:
        print('ended on iteration {}, length {}, dueDate {}, cost {}'.format(iter, methodResult.length, methodResult.dueDate, methodResult.cost))

    return methodResult
