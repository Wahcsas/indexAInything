def flatten_list(nested_list):
    """
    Recursively flattens a list of lists into a single list.

    :param nested_list: List with potentially nested lists
    :return: A flattened list
    """
    flattened = []
    for element in nested_list:
        if isinstance(element, list):
            flattened.extend(flatten_list(element))  # Recursively flatten sublists
        else:
            flattened.append(element)  # Append non-list elements directly
    return flattened
