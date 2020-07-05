# Sage
def comb_partitions(n, verbose=True):
    if verbose:
        print(f"r:", "r_partitions")
    r_partitions = {}
    for r in range(n):
        for l in range(0,r+1):
            r_partitions.setdefault(l, [])
            l_partitions = Partitions(r, length=l).list()
            # Sage .list() output is not a list, make it one
            l_partitions = [list(x) for x in l_partitions]
            r_partitions.get(l).extend(l_partitions)
    if verbose:
        for k,v in r_partitions.items():
            print(f"{k+1}:", v)
    return list(r_partitions.values())

# Deprecate for Sage multinomial function
def multiset_perms(k_counts):
    "Simple multinomial coefficient using standard lib `math` functions"
    n_factorial = factorial(sum(k_counts))
    k_count_factorial_prod = prod([factorial(x) for x in k_counts])
    n_perms = n_factorial/k_count_factorial_prod
    return int(n_perms)

def comb_partition_multinom_coeffs(n, verbose=True):
    if verbose:
        print(f"r:", "r_partition_coeffs")
    comb_pp = comb_partitions(n, verbose=False)
    partition_path_coeffs = {}
    for i, p_list in enumerate(comb_pp):
        kc_list = [[p.count(x) for x in set(p)] for p in p_list]
        multinoms = [multinomial(kcounts) for kcounts in kc_list]
        partition_path_coeffs.update({i: multinoms})
    empty_set = {0: []}
    partition_path_coeffs.update(empty_set)
    partition_path_coeffs = dict(sorted(partition_path_coeffs.items()))
    if verbose:
        for k,v in partition_path_coeffs.items():
            print(f"{k+1}:", v)
    return list(partition_path_coeffs.values())

def comb_partition_counts(n, multiplied=False, verbose=True):
    if verbose:
        print(f"r:", "r_partition_counts")
    comb_pp = comb_partitions(n, verbose=False)
    partition_path_counts = {}
    for i, p_list in enumerate(comb_pp):
        r = i+1 # `i` is 0-based `r`
        kc_list = [[p.count(x) for x in set(p)] for p in p_list]
        multinoms = [multinomial(kcounts) for kcounts in kc_list]
        if multiplied:
            counts = [(n-sum(p))*m for p, m in zip(p_list, multinoms)]
        else:
            counts = [(n-sum(p), m) for p, m in zip(p_list, multinoms)]
        partition_path_counts.update({i: counts})
    empty_set = {0: []}
    partition_path_counts.update(empty_set)
    partition_path_counts = dict(sorted(partition_path_counts.items()))
    if verbose:
        for k,v in partition_path_counts.items():
            print(f"{k+1}:", v)
    return list(partition_path_counts.values())
