import numpy as np
from options import result
from validator import calculate_ordering_cost
def tradeOffMethod(instance, debugPrinter):
    np.set_printoptions(precision=3)
    printer = debugPrinter
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
    #printer.print(instance.data[:, :6])
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
                printer.print('earliness: assigned {}, to assign {}'.format(tasksAssigned, earlinessArray[:,3]))
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
            printer.print('adding {}*{}'.format(lengthToDueDate, bestTask[1]))
            printer.print('iter {} -> earliness: chosen task id={}, x:{},a:{}, length {}, dueDate {}, cost {}, added:{}'.
                format(iter, bestTask[3], bestTask[0], bestTask[1], methodResult.length, methodResult.dueDate, methodResult.cost, costToAdd))
        else:
            #tardiness stage
            if not recalculatedTardinessArray:
                #take only not assigned elements
                tardinessArray = np.array([x for x in tardinessArray if x[3] not in tasksAssigned])
                recalculatedTardinessArray = True
                printer.print('tardiness: assigned {}, to assign {}'.format(tasksAssigned, tardinessArray[:,3]))

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
            #if methodResult.length < methodResult.dueDate and currentTardinessLength == 0 and iter > 1:
            #    lengthToDueDate = tasksLength - (methodResult.length + bestTask[0]) - (methodResult.dueDate - methodResult.length)
            #else:
            #    #tardiness phase was first
            lengthToDueDate = tardinessDueDate - currentTardinessLength

            methodResult.length += bestTask[0]
            currentTardinessLength += bestTask[0]
            costToAdd = lengthToDueDate*bestTask[2]
            methodResult.cost += costToAdd

            printer.print("adding {}*{}".format(lengthToDueDate, bestTask[2]))
            printer.print('iter {} -> tardiness: chosen task id={}, x:{},b:{}, length {}, dueDate {}, cost {}, added:{}'
                .format(iter, bestTask[3], bestTask[0], bestTask[2], methodResult.length, methodResult.dueDate, methodResult.cost, costToAdd))

        iter += 1

    tardinessAssigned.reverse()
    methodResult.order = tasksAssigned + tardinessAssigned
    printer.print("assigned tasks {}".format(methodResult.order))
    #if arguments['n'] > 20:
    #    tasksAssigned = []
    
    printer.print('ended on iteration {}, length {}, dueDate {}, cost {}'.format(iter, methodResult.length, methodResult.dueDate, methodResult.cost))

    return methodResult

def secondMethod(instance, debugPrinter):
    method_result = result(instance)
    total_length = sum(instance.data[:, 0])
    due_date = int(total_length * instance.h)

    #calculate length/penalty ratios
    #for an earliness
    instance.data[:, 4] = instance.data[:,0] / instance.data[:,1]
    # for a tardiness
    instance.data[:, 5] = instance.data[:,0] / instance.data[:,2]
    earliness_array = np.array(sorted(instance.data, key=lambda task: task[4], reverse=True)) #sort by the earliness ratio
    tardiness_array = np.array(sorted(instance.data, key=lambda task: task[5], reverse=True)) #sort by the tardiness ratio
    earliness_order = []
    tardiness_order = []
    already_assigned_tasks = []
    earliness_length = 0
    tardiness_length = 0
    earliness_iter = 0
    tardiness_iter = 0

    while method_result.length < total_length:
        best_earliness_option = earliness_array[earliness_iter]
        earliness_option_penalty = abs(due_date - earliness_length - best_earliness_option[0]) * best_earliness_option[1]

        best_tardiness_option = tardiness_array[tardiness_iter]
        tardiness_option_penalty = abs(due_date - (total_length - tardiness_length)) * best_tardiness_option[2]


        debugPrinter.print('cost {}, length {}\nearliness option id {} x {} a {} b {} earliness penalty {}, earliness ratio x/a {} x/b {}\ntardiness option id {} x {} a {} b {} tardiness penalty {}, tardiness ratio x/a {} x/b {}'
                           .format(method_result.cost, method_result.length,
                                   best_earliness_option[3], best_earliness_option[0], best_earliness_option[1], best_earliness_option[2], earliness_option_penalty, best_earliness_option[4], best_earliness_option[5],
                                   best_tardiness_option[3], best_tardiness_option[0], best_tardiness_option[1], best_tardiness_option[2], tardiness_option_penalty, best_tardiness_option[4], best_tardiness_option[5]))

        if earliness_option_penalty < tardiness_option_penalty:
            if earliness_length + best_earliness_option[0] <= due_date:
                earliness_length += add_task_to_array(best_earliness_option, method_result, earliness_order, earliness_option_penalty, already_assigned_tasks, debugPrinter)
                debugPrinter.print('earliness length is ok, earliness len {}, tardiness len {}'.format(earliness_length,
                                                                                                       tardiness_length))
                earliness_iter += 1
            else:
                #use best tardiness option in earliness part only when best tardiness option fits earliness part and tardiness length is longer than tardiness part
                if earliness_length + best_tardiness_option[0] <= due_date and tardiness_length > (total_length - due_date):
                    #calculate an earliness penalty using best tardiness option
                    earliness_penalty = (due_date - earliness_length - best_tardiness_option[0]) * best_tardiness_option[1]
                    earliness_length += add_task_to_array(best_tardiness_option, method_result, earliness_order, earliness_penalty, already_assigned_tasks, debugPrinter)
                    debugPrinter.print(
                        'earliness length is not ok (corrected earliness, earliness len {}, tardiness len {}'.format(
                            earliness_length, tardiness_length))
                    earliness_iter += 1
                else:
                    tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order, tardiness_option_penalty, already_assigned_tasks, debugPrinter)
                    debugPrinter.print(
                        'earliness length is not ok, earliness len {}, tardiness len {}'.format(earliness_length,
                                                                                                tardiness_length))
                    tardiness_iter += 1
        else:
            if tardiness_length <= (total_length - due_date) and best_tardiness_option[5] >= best_earliness_option[4]:
                tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order, tardiness_option_penalty, already_assigned_tasks, debugPrinter)
                debugPrinter.print('tardiness length is ok, earliness len {}, tardiness len {}'.format(earliness_length,
                                                                                                       tardiness_length))
                tardiness_iter += 1
            else:
                earliness_length += add_task_to_array(best_earliness_option, method_result, earliness_order, earliness_option_penalty, already_assigned_tasks, debugPrinter)
                debugPrinter.print(
                    'tardiness length is not ok, earliness len {}, tardiness len {}'.format(earliness_length,
                                                                                            tardiness_length))
                earliness_iter += 1

    method_result.order = earliness_order + list(reversed(tardiness_order))
    calculate_ordering_cost(instance, method_result.order)
    return method_result


def add_task_to_array(task, method_result, order_array, penalty, already_assigned_tasks, debug_printer):
    if task[3] in already_assigned_tasks:
        debug_printer.print("task {} already taken".format(task[3]))
        return 0  # add 0 to the length, but increase iterator
    method_result.cost += penalty
    order_array.append(int(task[3]))  # append id
    method_result.length += task[0]  # add length of this task
    already_assigned_tasks.append(task[3])
    return task[0]

