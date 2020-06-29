from more_itertools import powerset
from numpy import ediff1d

def ps_sorter(tup):
    l = len(tup)
    d = ediff1d(tup).tolist()
    return l, d

ps = powerset([1,2,3,4])

ps = sorted(ps, key=ps_sorter)

for x in ps:
    print(x)
