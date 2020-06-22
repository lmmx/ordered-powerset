# Ordered powersets

**Note**: The combinations provided by Python's `itertools.combinations`
are not ordered in the way I'd expect, and I wasn't aware of
`more_itertools.powerset` at the time of needing this code, so I
wrote this fast version (I'm not sure how the `more_itertools`
version compares but I doubt it does poorly).

This code is equivalent to the program I wrote and much simpler, therefore
I recommend that instead:

```py
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
```
⇣
```py
()
(1,)
(2,)
(3,)
(4,)
(1, 2)
(2, 3)
(3, 4)
(1, 3)
(2, 4)
(1, 4)
(1, 2, 3)
(2, 3, 4)
(1, 2, 4)
(1, 3, 4)
(1, 2, 3, 4)
```

Original code README follows:

---

I need to generate powersets of `n` items, so I wrote this code to
provide the ordered powerset such that the sequence progresses in
a sorted order with respect to (firstly) the sum of the indices of
the subset elements, and the index of the subset elements, both
in ascending order.

Here's an example with the first 6 letters of the alphabet:

```sh
python string_powerset.py abcdef
```
⇣
```STDOUT
a, b, c, d, e, f

ab, bc, cd, de, ef
ac, bd, ce, df
ad, be, cf
ae, bf
af

abc, bcd, cde, def
abd, bce, cdf
acd, bde, cef
abe, bcf
ade, bef
ace, bdf
abf
aef
acf
adf

abcd, bcde, cdef
abce, bcdf
abde, bcef
acde, bdef
abcf
abef
adef
abdf
acdf
acef

abcde, bcdef
abcdf
abcef
abdef
acdef

abcdef
```
