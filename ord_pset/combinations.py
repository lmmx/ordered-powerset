from itertools import combinations
import numpy as np

items = list("abcdef")
c_dict = dict()
uc_dict = dict()

def max_diff_min(itemstr):
    indexes = [items.index(char) for char in itemstr]
    if len(indexes) > 1:
        gap_counts = np.ediff1d(indexes).tolist()
        mdm = min(gap_counts), tuple(gap_counts)
    else:
        mdm = 0, tuple()
    return mdm

def ordered_combinations(items, r):
    combs = combinations(items, r)
    oc = sorted(combs, key=max_diff_min)
    return oc

for i in range(1, len(items)+1):
    comb_dict = {i-1: []}
    for r in range(1,i):
        for c in ordered_combinations(items, r):
            comb_str = "".join(c)
            comb_dict[i-1].append(comb_str)
    c_dict.update(comb_dict)

for i in range(1, len(items)+1):
    u_comb_dict = {i-1: []}
    for r in range(1,i):
        for c in combinations(items, r):
            comb_str = "".join(c)
            u_comb_dict[i-1].append(comb_str)
    uc_dict.update(u_comb_dict)

def print_num_tuple_list(num_tuple_list):
    tup_repr = "  ".join(repr([repr(pos).replace(" ","") for pos in
        num_tuple_list]).replace("'","").replace(",","").split())
    print(" "+tup_repr[1:-1])
    return

def print_pos_diffs(pos_diffs):
    print("  "+(")   (".join(repr(pos_diffs).replace(", ",
        "").split(")("))[1:-1]).replace("(", " ").replace(")"," "))
    return

def vals_to_pos_tup_list(vals_str_list):
    pos_tup_list = [tuple([items.index(x) for x in v]) for v in vals_str_list]
    return pos_tup_list

def pos_list_to_diffs(pos_list):
    diffs = [tuple(np.ediff1d(x)) for x in pos_list]
    return diffs

four_vals = [x for x in c_dict[4] if len(x) > 3]
fv_pos = vals_to_pos_tup_list(four_vals)
fv_diffs = pos_list_to_diffs(fv_pos)

u_four_vals = [x for x in uc_dict[4] if len(x) > 3]
ufv_pos = vals_to_pos_tup_list(u_four_vals)
ufv_diffs = pos_list_to_diffs(ufv_pos)

print(four_vals)
print_num_tuple_list(fv_pos)
print_pos_diffs(fv_diffs)
print()
print(u_four_vals)
print_num_tuple_list(ufv_pos)
print_pos_diffs(ufv_diffs)
