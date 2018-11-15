import numpy as np
from options import Result
from validator import calculate_ordering_cost


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

        debug_printer.log(
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
            debug_printer.log(
                'earliness priority, earliness len {}, tardiness len {}'.format(earliness_length, tardiness_length))
            earliness_iter += 1
            continue
        if instance.h < .5 and tardiness_length/total_length < 2*(1-instance.h) - 1:
            tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order,
                                                  tardiness_option_penalty, already_assigned_tasks,
                                                  debug_printer)
            debug_printer.log(
                'tardiness priority, earliness len {}, tardiness len {}'.format(earliness_length, tardiness_length))
            tardiness_iter += 1
            continue

        if earliness_option_penalty < tardiness_option_penalty:
            if earliness_length + best_earliness_option[0] <= due_date:
                earliness_length += add_task_to_array(best_earliness_option, method_result, earliness_order,
                                                      earliness_option_penalty, already_assigned_tasks, debug_printer)
                debug_printer.log('earliness length is ok, earliness len {}, tardiness len {}'
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
                    debug_printer.log(
                        'earliness length is not ok (corrected earliness, earliness len {}, tardiness len {}'
                            .format(earliness_length, tardiness_length))
                    earliness_iter += 1
                else:
                    tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order,
                                                          tardiness_option_penalty, already_assigned_tasks,
                                                          debug_printer)
                    debug_printer.log(
                        'earliness length is not ok, earliness len {}, tardiness len {}'
                            .format(earliness_length, tardiness_length))
                    tardiness_iter += 1
        else:
            if tardiness_length <= (total_length - due_date) and best_tardiness_option[5] >= best_earliness_option[4]:
                tardiness_length += add_task_to_array(best_tardiness_option, method_result, tardiness_order,
                                                      tardiness_option_penalty, already_assigned_tasks, debug_printer)
                debug_printer.log('tardiness length is ok, earliness len {}, tardiness len {}'
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
                    debug_printer.log('2tardiness length is ok, earliness len {}, tardiness len {}'
                                        .format(earliness_length, tardiness_length))
                    tardiness_iter += 1
                else:
                    earliness_length += add_task_to_array(best_earliness_option, method_result, earliness_order,
                                                          earliness_option_penalty, already_assigned_tasks, debug_printer)
                    debug_printer.log('tardiness length is not ok, earliness len {}, tardiness len {}'
                                        .format(earliness_length, tardiness_length))
                    earliness_iter += 1

    method_result.order = earliness_order + list(reversed(tardiness_order))
    return method_result


def add_task_to_array(task, method_result, order_array, penalty, already_assigned_tasks, debug_printer):
    if task[3] in already_assigned_tasks:
        debug_printer.log("task {} already taken".format(task[3]))
        return 0  # add 0 to the length, but increase iterator
    method_result.cost += penalty
    order_array.append(int(task[3]))  # append id
    method_result.length += task[0]  # add length of this task
    already_assigned_tasks.append(task[3])
    return task[0]