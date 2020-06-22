from pprinting import pprint_tuple
from itertools import permutations as permute
from numpy import cumsum

# http://jeromekelleher.net/generating-integer-partitions.html
# via
# https://stackoverflow.com/questions/10035752/elegant-python-code-for-integer-partitioning#comment25080713_10036764

def asc_int_partitions(n):
    a = [0 for i in range(n + 1)]
    k = 1
    y = n - 1
    while k != 0:
        x = a[k - 1] + 1
        k -= 1
        while 2 * x <= y:
            a[k] = x
            y -= x
            k += 1
        l = k + 1
        while x <= y:
            a[k] = x
            a[l] = y
            yield tuple(a[:k + 2])
            x += 1
            y -= 1
        a[k] = x + y
        y = x + y - 1
        yield tuple(a[:k + 1])

# https://stackoverflow.com/a/6285330/2668831
def uniquely_permute(iterable, enforce_sort=False, r=None):
    previous = tuple()
    if enforce_sort: # potential waste of effort (default: False)
        iterable = sorted(iterable)
    for p in permute(iterable, r):
        if p > previous:
            previous = p
            yield p

def print_partitions(max_n, permuting=False):
    for n in range(max_n):
        partition_list = list(asc_int_partitions(n))
        for p in partition_list:
            if permuting:
                perms = uniquely_permute(p)
                for perm in perms:
                    print(pprint_tuple(perm), end=" ")
            else:
                print(pprint_tuple(p), end=" ")
        print()
    return

def sum_min(p):
    return sum(p), min(p)

def partitions_by_length(max_n, sorting=True, permuting=False):
    partition_dict = {0: ()}
    for n in range(1,max_n+1):
        partition_dict.setdefault(n, [])
        partitions = list(asc_int_partitions(n))
        for p in partitions:
            if permuting:
                perms = uniquely_permute(p)
                for perm in perms:
                    partition_dict.get(len(p)).append(perm)
            else:
                partition_dict.get(len(p)).append(p)
    if not sorting:
        return partition_dict
    for k in partition_dict:
        partition_dict.update({k: sorted(partition_dict.get(k), key=sum_min)})
    return partition_dict

def print_partitions_by_length(max_n, sorting=True, permuting=True):
    partition_dict = partitions_by_length(max_n, sorting=sorting, permuting=permuting)
    for k in partition_dict:
        if k == 0:
            print(tuple(partition_dict.get(k)), end="")
        for p in partition_dict.get(k):
            print(pprint_tuple(p), end=" ")
        print()
    return

def generate_powerset(items, subset_handler=tuple, verbose=False):
    """
    Generate the powerset of an iterable `items`.

    Handling of the elements of the iterable is by whichever function is passed as
    `subset_handler`, which must be able to handle the `None` value for the
    empty set. The function `string_handler` will join the elements of the subset
    with the empty string (useful when `items` is an iterable of `str` variables).
    """
    ps = {0: [subset_handler()]}
    n = len(items)
    p_dict = partitions_by_length(n-1, sorting=True, permuting=True)
    for p_len, parts in p_dict.items():
        ps.setdefault(p_len, [])
        if p_len == 0:
            # singletons
            for offset in range(n):
                subset = subset_handler([items[offset]])
                if verbose:
                    if offset > 0:
                        print(end=" ")
                    if offset == n - 1:
                        print(subset, end="\n")
                    else:
                        print(subset, end=",")
                ps.get(p_len).append(subset)
        for pcount, partition in enumerate(parts):
            distance = sum(partition)
            indices = (cumsum(partition)).tolist()
            for offset in range(n - distance):
                subset = subset_handler([items[offset]] + [items[offset:][i] for i in indices])
                if verbose:
                    if offset > 0:
                        print(end=" ")
                    if offset == n - distance - 1:
                        print(subset, end="\n")
                    else:
                        print(subset, end=",")
                ps.get(p_len).append(subset)
        if verbose and p_len < n-1:
            print()
    return ps

def string_handler(x=None):
    if x is None:
        t = tuple()
    else:
        t = tuple(x)
    return "".join(t)
