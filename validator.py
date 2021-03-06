from options import Result


def validate_result(instance, order):
    if len(order) > instance.n:
        print('There are too many elements. {} > {}'.format(len(order), instance.n))
        return Result(instance)

    if len(order) < instance.n:
        temp = [x for x in range(instance.n) if x not in order]
        print("There are no all elements in order {} != {}. Missing task {}".format(len(order), instance.n, temp))
        return Result(instance)

    if len(set(order)) != len(order):
        temp = []
        err = []
        for i in order:
            if i in temp:
                err.append(i)
            temp.append(i)
        print(
            "There is at least one task that is occurs at least twice.\nElements that occur more than once: {}"
                .format(err))
        return Result(instance)
    validation_result = calculate_ordering_cost(instance, order)
    assert validation_result.length == sum([x.length for x in instance.data]), "Total length is not correct"
    return validation_result


def calculate_ordering_cost(instance, order):
    validation_result = Result(instance)
    validate_result.order = order
    total_length = sum([x.length for x in instance.data])
    due_date = int(instance.h * total_length)
    for item in order:
        task = list(filter(lambda x : x.task_index == item, instance.data))[0]
        validation_result.length += task.length
        distance_to_due_date = abs(due_date - validation_result.length)
        if validation_result.length <= due_date:
            validation_result.cost += distance_to_due_date * task.earliness_cost  # penalty for an earliness
        else:
            validation_result.cost += distance_to_due_date * task.tardiness_cost  # penalty for a tardiness
    return validation_result
