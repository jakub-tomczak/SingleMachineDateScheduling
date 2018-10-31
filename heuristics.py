import numpy as np
from options import Result
from validator import calculate_ordering_cost


def trade_off_method(instance, debug_printer):
    np.set_printoptions(precision=3)
    printer = debug_printer
    method_result = Result(instance)
    # arguments to local vars
    tasks_length = sum([x[0] for x in instance.data])  # sum by index 0 => task's length
    method_result.dueDate = int(instance.h * tasks_length)

    # calculate length/penalty ratios
    # for an earliness
    instance.data[:, 4] = instance.data[:, 0] / instance.data[:, 1]
    # for a tardiness
    instance.data[:, 5] = instance.data[:, 0] / instance.data[:, 2]

    earliness_array = np.array(
        sorted(instance.data, key=lambda task: task[4], reverse=True))  # sort by the earliness ratio
    tardiness_array = np.array(
        sorted(instance.data, key=lambda task: task[5], reverse=True))  # sort by the tardiness ratio
    # printer.print(instance.data[:, :6])
    # iteration of the algorithm
    iter = 0

    # flag that indicates whether we've recalculated
    # tardiness penalties and removed already assigned tasks (in the earliness stage)
    # if h>.5 we start from earliness stage so recalculating earliness_array is not necessary
    recalculated_tardiness_array = instance.h < .5
    recalculated_earliness_array = instance.h > .5

    # indices of assigned tasks
    tasks_assigned = []
    # tardiness should be reversed
    tardiness_assigned = []

    # do we start from the earliness stage?
    earliness_stage = instance.h > .5

    tardiness_due_date = tasks_length - method_result.dueDate
    current_tardiness_length = 0

    while method_result.length < tasks_length and iter < instance.n + 1:
        if earliness_stage:
            if not recalculated_earliness_array:
                # take only not assigned elements
                earliness_array = np.array([x for x in earliness_array if x[3] not in tardiness_assigned])
                printer.print('earliness: assigned {}, to assign {}'.format(tasks_assigned, earliness_array[:, 3]))
                recalculated_earliness_array = True
            # x[4] - task's length to earliness penalty ratio
            # x[6]==1 task has been already assigned

            # take only not assigned tasks
            # if h<.5 then earliness stage is the second one so we don't care about the limit
            earliness_array = np.array([x for x in earliness_array if x[6] != 1 and
                                       (instance.h < 0.5 or x[0] + method_result.length <= method_result.dueDate)])

            # found no candidates for the best_task, continue in tardiness stage
            if len(earliness_array) == 0:
                earliness_stage = False
                iter += 1
                continue

            best_task = earliness_array[0]
            # add task to the list
            tasks_assigned.append(int(best_task[3]))  # [3] -> task's index
            # and mark it as used
            best_task[6] = 1  # TODO rewrite it, in order not to use a number as a flag -> it's float!
            method_result.length += best_task[0]

            # put cost to add to another variable for debug purposes
            if method_result.length < method_result.dueDate:
                # earliness stage was first
                length_to_due_date = method_result.dueDate - method_result.length
            else:
                length_to_due_date = method_result.dueDate - (method_result.length - current_tardiness_length)
            cost_to_add = length_to_due_date * best_task[1]
            method_result.cost += cost_to_add
            printer.print('adding {}*{}'.format(length_to_due_date, best_task[1]))
            printer.print(
                'iter {} -> earliness: chosen task id={}, x:{},a:{}, length {}, dueDate {}, cost {}, added:{}'.
                format(iter, best_task[3], best_task[0], best_task[1], method_result.length, method_result.dueDate,
                       method_result.cost, cost_to_add))
        else:
            # tardiness stage
            if not recalculated_tardiness_array:
                # take only not assigned elements
                tardiness_array = np.array([x for x in tardiness_array if x[3] not in tasks_assigned])
                recalculated_tardiness_array = True
                printer.print('tardiness: assigned {}, to assign {}'.format(tasks_assigned, tardiness_array[:, 3]))

            # if h>0.5 then we don't care about the size - earliness stage was first
            tardiness_array = np.array([x for x in tardiness_array if x[6] != 1 and
                            (instance.h > 0.5 or (tasks_length - method_result.dueDate) - method_result.length >= 0)])
            # otherwise check if current task is not longer than the total time for tardiness stage

            # found no candidates for the best_task, continue in earliness stage
            if len(tardiness_array) == 0:
                # TODO check if earliness stage has been performed already in order to finish
                earliness_stage = True
                iter += 1
                continue

            best_task = tardiness_array[0]
            tardiness_assigned.append(int(best_task[3]))  # [3] -> index
            best_task[6] = 1  # TODO rewrite it, in order not to use a number as a flag -> it's float!

            length_to_due_date = tardiness_due_date - current_tardiness_length

            method_result.length += best_task[0]
            current_tardiness_length += best_task[0]
            cost_to_add = length_to_due_date * best_task[2]
            method_result.cost += cost_to_add

            printer.print("adding {}*{}".format(length_to_due_date, best_task[2]))
            printer.print('iter {} -> tardiness: chosen task id={}, x:{},b:{}, length {}, dueDate {}, cost {}, added:{}'
                          .format(iter, best_task[3], best_task[0], best_task[2], method_result.length,
                                  method_result.dueDate, method_result.cost, cost_to_add))

        iter += 1

    tardiness_assigned.reverse()
    method_result.order = tasks_assigned + tardiness_assigned
    printer.print("assigned tasks {}".format(method_result.order))
    printer.print(
        'ended on iteration {}, length {}, dueDate {}, cost {}'
            .format(iter, method_result.length, method_result.dueDate, method_result.cost))

    return method_result


def second_method(instance, debug_printer):
    method_result = Result(instance)
    total_length = sum(instance.data[:, 0])
    due_date = int(total_length * instance.h)

    # calculate length/penalty ratios
    # for an earliness
    instance.data[:, 4] = instance.data[:, 0] / instance.data[:, 1]
    # for a tardiness
    instance.data[:, 5] = instance.data[:, 0] / instance.data[:, 2]
    earliness_array = np.array(
        sorted(instance.data, key=lambda task: task[4], reverse=True))  # sort by the earliness ratio
    tardiness_array = np.array(
        sorted(instance.data, key=lambda task: task[5], reverse=True))  # sort by the tardiness ratio
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

        debug_printer.print(
            'cost {}, length {}\nearliness option id {} x {} a {} b {} earliness penalty {}, earliness ratio x/a {} x/b {}\ntardiness option id {} x {} a {} b {} tardiness penalty {}, tardiness ratio x/a {} x/b {}'
            .format(method_result.cost, method_result.length,
                    best_earliness_option[3], best_earliness_option[0], best_earliness_option[1],
                    best_earliness_option[2], earliness_option_penalty, best_earliness_option[4],
                    best_earliness_option[5],
                    best_tardiness_option[3], best_tardiness_option[0], best_tardiness_option[1],
                    best_tardiness_option[2], tardiness_option_penalty, best_tardiness_option[4],
                    best_tardiness_option[5]))

        # if h > .5 then assign before due date, as long as remaining length before and after due date are equal
        if instance.h > .5 and earliness_length/total_length < 2*instance.h-1:
            # assign only from beginning
            earliness_length += add_task_to_array(best_earliness_option, method_result, earliness_order,
                                                  earliness_option_penalty, already_assigned_tasks,
                                                  debug_printer)
            debug_printer.print(
                'earliness priority, earliness len {}, tardiness len {}'.format(earliness_length, tardiness_length))
            earliness_iter += 1
            continue
        if instance.h < .5 and tardiness_length/total_length < 2*(1-instance.h) - 1:
            tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order,
                                                  tardiness_option_penalty, already_assigned_tasks,
                                                  debug_printer)
            debug_printer.print(
                'tardiness priority, earliness len {}, tardiness len {}'.format(earliness_length, tardiness_length))
            tardiness_iter += 1
            continue

        if earliness_option_penalty < tardiness_option_penalty:
            if earliness_length + best_earliness_option[0] <= due_date:
                earliness_length += add_task_to_array(best_earliness_option, method_result, earliness_order,
                                                      earliness_option_penalty, already_assigned_tasks, debug_printer)
                debug_printer.print('earliness length is ok, earliness len {}, tardiness len {}'
                                    .format(earliness_length, tardiness_length))
                earliness_iter += 1
            else:
                # use best tardiness option in earliness part only when best
                # tardiness option fits earliness part and tardiness length is longer than tardiness part
                if earliness_length + best_tardiness_option[0] <= due_date \
                        and tardiness_length > (total_length - due_date):
                    # calculate an earliness penalty using best tardiness option
                    earliness_penalty = (due_date - earliness_length - best_tardiness_option[0]) * \
                                        best_tardiness_option[1]
                    earliness_length += add_task_to_array(best_tardiness_option, method_result, earliness_order,
                                                          earliness_penalty, already_assigned_tasks, debug_printer)
                    debug_printer.print(
                        'earliness length is not ok (corrected earliness, earliness len {}, tardiness len {}'
                            .format(earliness_length, tardiness_length))
                    earliness_iter += 1
                else:
                    tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order,
                                                          tardiness_option_penalty, already_assigned_tasks,
                                                          debug_printer)
                    debug_printer.print(
                        'earliness length is not ok, earliness len {}, tardiness len {}'
                            .format(earliness_length, tardiness_length))
                    tardiness_iter += 1
        else:
            if tardiness_length <= (total_length - due_date) and best_tardiness_option[5] >= best_earliness_option[4]:
                tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order,
                                                      tardiness_option_penalty, already_assigned_tasks, debug_printer)
                debug_printer.print('tardiness length is ok, earliness len {}, tardiness len {}'
                                    .format(earliness_length, tardiness_length))
                tardiness_iter += 1
            else:
                if earliness_length + best_earliness_option[0] > due_date:
                    earliness_iter += 1
                    if tardiness_length > (total_length - due_date):
                        continue
                    tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order,
                                                          tardiness_option_penalty, already_assigned_tasks,
                                                          debug_printer)
                    debug_printer.print('2tardiness length is ok, earliness len {}, tardiness len {}'
                                        .format(earliness_length, tardiness_length))
                    tardiness_iter += 1
                else:
                    earliness_length += add_task_to_array(best_earliness_option, method_result, earliness_order,
                                                          earliness_option_penalty, already_assigned_tasks, debug_printer)
                    debug_printer.print('tardiness length is not ok, earliness len {}, tardiness len {}'
                                        .format(earliness_length, tardiness_length))
                    earliness_iter += 1

    method_result.order = earliness_order + list(reversed(tardiness_order))
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


def sort_by_order(method_result):
    final_matrix = np.zeros(method_result.instance.data.shape)
    for i in range(method_result.instance.n):
        final_matrix[i, :] = method_result.instance.data[method_result.order[i], :]
    return final_matrix
