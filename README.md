# Ordered powersets

**Note**: The combinations provided by Python's `itertools.combinations`
are not ordered in the way I'd expect, and I wasn't aware of
`more_itertools.powerset` at the time of needing this code, so I
wrote this fast version (I'm not sure how the `more_itertools`
version compares but I doubt it does poorly).

- This code was posted [on StackOverflow](https://stackoverflow.com/a/62521582/2668831)
- Section 2 of this README looks at representing this order as a Gray code,
  by converting the sequence of integers (the index of the items in the input set)
  to a binary bitstream using the `bitstring` package.
  - [Skip the intro](#Efficient_bitstream_processing_method)

The `more_itertools.powerset` function is listed in the `itertools` [recipes
page](https://docs.python.org/3/library/itertools.html#itertools-recipes):

```py
def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))
```

- The use of `r` indicates the size of the subset and the lower part of a binomial
  coefficient (the upper part is usually "n" rather than `s` as here). Most calculators
  have “n Choose r”.

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

---

## Efficient bitstream processing method

Now that we've generated them in the proper order, it's worth reiterating what we did.

Forgetting about the order for a second, the difference between enumerating all combinations 
of the input set `{1, …, n}` without rearrangement (i.e. all subsets, i.e. the power set) and
enumerating all combinations with rearrangement (i.e. all possible orderings of all subsets)
can be stated in terms of the index positions of the items.

In terms of the index positions, we obtained all ascending combinations (and this is visibly
apparent in the original output, where the combinations are in lexicographical order).

E.g. for 4 items, the index positions of the items `{1, …, n}` are `{1,2,3,4}`, and the powerset
was:

```STDOUT
1, 2, 3, 4

12, 13, 14
23, 24

123, 124, 134
234

1234
```

Every other possible combination (_with_ rearrangements of those listed above) has one or more
[_descents_](https://en.wikipedia.org/wiki/Permutation#Ascents%2C_descents%2C_runs_and_excedances),
i.e. positions where the subsequent element in the subset is a lower position in the original item
set.

- E.g. 21 is a rearrangement of 12, and has a descent at the first [1-based] position, `2`, as the
  subsequent position (the 2nd) is lower than it (`1 < 2`).
  - and so on for the other possible rearrangements: `31, 41, 32, 42, 321, 421, ...` etc.

When we changed the order of this powerset (which we now call all of the "ascending combinations"),
like so:

```sh
python string_powerset.py 1234
```
⇣
```STDOUT
1, 2, 3, 4

12, 23, 34
13, 24
14

123, 234
124
134

1234
```

We took this set _out_ of ascending lexicographic order: we obtained the "ascending combinations"
in non-monotonically ascending lexicographic order.

This order is not colexicographic either (a.k.a. "colex"), which is when you sort the numbers in
'reverse reading direction', i.e. you sort 12 as if it were 21, sort 123 as if it were 321, etc.

- In colex order, `124 < 234` (∵ in lexicographic order, `421 < 432`) whereas in our order,
  `234 < 124` (as our order is based on both length and position distances, and they are the same
  length, `3 = 3`, but the sum of position distances is `1+1 = 2` for 234 and `1+2 = 3` for 124,
  ∴ `234 < 124` in our minimal-distance ordering ∵ `2 < 3` lexicographically)

- See: OEIS Wiki ⠶ [Orderings ⠶ Colexicographic_order](https://oeis.org/wiki/Orderings#Colexicographic_order)

Now that we've ascertained that we want the "ascending combinations" (i.e. without
descents, in the terminology of permutations), and we want these ascending combinations "out of
[lexicographically] ascending order", and also not in colex order, I'm curious what the order is.

One way to get more information on the properties of the order is with a binary code, known as
[Gray code](https://en.wikipedia.org/wiki/Gray_code). To obtain this, we simply convert the
powerset sequence in our desired order to a binary stream (i.e. the concatenation of binary
bitstrings).

This is easily done with the `bitstring` package's `Bits` class, e.g. `Bits(uint=2, length=2).bin`⇢`'10'`.

One nice feature of the `Bits` class is that while we can expose a nice string with `.bin`

- ...rather than having to `.lstrip("0b")` if we used the builtin `bin(2)`⇢`'0b10'`,
- ...and also without having to manually pad the left hand side when we want bitstrings of matching
  length in a range, e.g. `[bin(i) for i in range(3)]` ⇢ `['0b0', '0b1', '0b10']` doesn't pad the
  start of the first two bitstrings with a zero.

...we can access an iterator, which means _we don't have to pull the entire bitstream into memory_!
\*

- \* Maybe: I'm not sure what `ConstByteStore` is but it's not a list and we don't need to make it
  one, presumably using it as a generator is more efficient than accessing `.bin` on it and ignoring
  all except the sub-bitstring we want)
  - On closer inspection, the class docstring says "Used internally - not part of public interface",
    and one of the methods describes having "direct access to byte data", which probably means this
    is as efficient as you can get, and should try and consume only this if possible, without
    making duplicate copies elsewhere if we're trying to be memory efficient.

This can then be paired up to methods which efficiently consume iterators such as the (new and
exciting, only 1 year old) `more_itertools.ichunked` function which also doesn't load an iterator
into RAM, but instead — so long as the source iterator is accessed in order — only loads
sub-iterators into RAM.

- This means that when we have a very long `BitStream`, rather than loading it as a string,
  we can just access the generator, and only touch the byte data we need, allowing Python
  to garbage collect the memory for those bytes once the sub-iterator advances.

```sh
python -i bit_strings.py
```
⇣
```py
>>> bs = bitstream_ins(range(1))
>>> bs = bitstream_ins(range(1))
>>> bs
BitStream('0b0')
>>> bs.bin
'0'
>>> bs = bitstream_ins(range(2))
>>> bs
BitStream('0b01')
>>> bs.bin
'01'
>>> bs = bitstream_ins(range(9))
>>> bs
BitStream('0b0110111001011101111000')
>>> bs.bin
'0110111001011101111000'
>>> bs.len
22
>>> from itertools import accumulate
>>> from functools import reduce
>>> max(accumulate([bitstr_len(x) for x in range(9)]))
22
>>> reduce(lambda x, y: x + bitstr_len(y), range(9), 0)
22
```

The last two lines are two ways to calculate the length (`functools.reduce` only
returns the last value, `itertools.accumulate` yields all intermediate values,
i.e. all substring positions for the binary-encoded integers in our range).
