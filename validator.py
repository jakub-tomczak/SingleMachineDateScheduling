from options import result


def validate_result(instance, order):
    if len(order) > instance.n:
        print('There are too many elements. {} > {}'.format(len(order), instance.n))
        return result(instance)

    if len(order) < instance.n:
        temp = [x for x in range(instance.n) if x not in order]
        print("There are no all elements in order {} != {}. Missing task {}".format(len(order), instance.n, temp))
        return result(instance)

    if len(set(order)) != len(order):
        temp = []
        err = []
        for i in order:
            if i in temp:
                err.append(i)
            temp.append(i)
        print("There is at least one task that is occurs at least twice.\nElements that occur more than once: {}".format(err))
        return result(instance)
    validation_result = calculate_ordering_cost(instance, order)
    assert validation_result.length == sum(instance.data[:, 0]), "Total length is not correct"
    return validation_result


def calculate_ordering_cost(instance, order):
    validation_result = result(instance)
    validate_result.order = order
    total_length = sum(instance.data[:, 0])
    due_date = int(instance.h*total_length)
    for item in order:
        validation_result.length += instance.data[item, 0]
        distance_to_due_date = abs(due_date - validation_result.length)
        if validation_result.length <= due_date:
            validation_result.cost += distance_to_due_date * instance.data[item, 1] #penalty for an earliness
        else:
            validation_result.cost += distance_to_due_date * instance.data[item, 2] #penalty for a tardiness
    return validation_result