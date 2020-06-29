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

```sh
python string_powerset.py 123 | sed "/^$/d" | tr '\n' ',' | tr -d ' ' | sed 's/,$/\n/'
```
⇣
```STDOUT
1,2,3,12,23,13,123
```

We can then use this ordered powerset to obtain the Gray code for 3 items (`n=3`)

```py
>>> bs = bitstream_ins([1,2,3,12,23,13,123])
BitStream('0b1101111001011111011111011')
>>> bs.bin
'1101111001011111011111011'
```

This is fairly long, and can be shortened by "lencoding"
- (not sure what its proper name is, but I doubt I've invented anything new here)

```py
>>> bs = 
```

I.e. rather than using the set of codewords `{0,1}⁺` (ITILA p.92) so that `range(6)`
is represented by the bitstrings `{0,1,10,11,100,101}`, the first `n` bitstrings
from the union of the sets of codewords `⋃ { {0,1}ⁱ }` for all `i ∊ range(n)`

- Here `n` = 3 (the number of items in the identity set `{1,2,3}`, and `range(n)`
  is the [0-based] integer range `{0,1,2}` which in binary codewords _with_ lencoding
  becomes `{0,1,00}`

The obvious consequence is that unlike the `{0,1}⁺` codewords, the lencoded codewords
(let's call them `{0,1}⁺⁺` for now to suggest incrementation upon `{0,1}⁺`) repeat
binary values (but importantly, never with the same length bitstring), meaning that
for all but the first two bitstrings `{0,1}`, the binary value is lower than the
decoded integer value.

The offset of the lencoded binary value from its 'real' (decoded) integer value is
obtained as `2^(⌊log₂(3+2)⌋)-2` from the function `bitstr_lencoded_value_offset`
for the 0-based decoded integer value.

```py
bs_lossless = bitstream_ins(n=6)
bs_lencode = bitstream_ins(n=6, lencode=True)
bs_fixedlen = bitstream_ins(n=6, fixed_length=True)

print("Lossless:    ", bs_lossless.bin)
print("Lencoded:    ", bs_lencode.bin)
print("Fixed length:", bs_fixedlen.bin)
```
⇣
```STDOUT
Lossless:     011011100101
Lencoded:     0100011011
Fixed length: 000001010011100101
```

- To split those out into their codeword sets:

```
Lossless:      011011100101        =  {0,1,10,11,100,101}
Lencoded:      0100011011          =  {0,1,00,01,10,11}
Fixed length:  000001010011100101  =  {000,001,010,011,100,101}
```

- `TODO`: obtain these codeword sets by a function that iterates over the range
  and obtains split positions according to the `lenfunc(b)` for each `b` in the
  bit range

The remaining step is to not only output a range, or to count iterables and output
the range of the iterable's length (so as to count the items in the iterable), but
also to output only some within a range, and to begin to think about obtaining a
Gray code for the combinations in the order we want (comparing this order to the
'lexicographic' order we are able to get with the range).

In other words, we want an iterator which is not a `range_iterator`. We'll come back to this.

---

Earlier we determined the sequence to be reproduced, which we can print again with
the newlines removed and the blank lines replaced by `.`

```sh
python string_powerset.py 1234 | sed -e 's/^$/./g' | tr '\n' ',' | sed 's/,.,/./g' | tr -d ' '
```
⇣
```STDOUT
1,2,3,4.12,23,34,13,24,14.123,234,124,134.1234
```

It's pretty clear that we should be looking at this in binary, which is now possible by
passing these numbers to `bitstream_ins` (removing the `.` which was to show change of bitstring
length):

- I've now turned this into a package rather than scripts, so run with `python -im ord_pset`
  (to run interactively) or `import ord_pset` in a program in the top-level directory of this repo
  to reproduce
  - E.g. for the following, run `python print_combs_gen_code.py`
    - Side note: I went away and wrote the [mdblocks](https://github.com/lmmx/mdblocks)
      utility to make these output blocks at this point!
    - E.g. the one below came from `pybtickblock print_combs_gen_code.py`
    - To reproduce without `mdblocks` functions, just run as `python` and ignore any flags

```py
from ord_pset import bit_strings

gen = [[1,2,3,4],[12,23,34,13,24,14],[123,234,124,134],[1234]]
print(gen, end="\n⇣\n")

bs = bit_strings.BitStream()
split_bs = []
individual_bit_levels = []

for g in gen:
    bit_strings.bitstream_ins(g, bstream=bs)
    split_bs.append(bit_strings.bitstream_ins(g))
    individual_bitstrings = []
    for v in g:
        b = bit_strings.bitstream_ins([v])
        individual_bitstrings.append(b.bin)
    jb = ",".join(individual_bitstrings)
    individual_bit_levels.append(jb)

print(bs.bin)
print(".".join(individual_bit_levels))

jib = "".join(individual_bit_levels).replace(",","")
assert(jib == bs.bin), ValueError(
    "The individual bitstrings don't concatenate into the bitstream")
print("Concatenating the individual bitstrings matches the bitstream")
```
⇣
```STDOUT
[[1, 2, 3, 4], [12, 23, 34, 13, 24, 14], [123, 234, 124, 134], [1234]]
⇣
11011100110010111100010110111000111011110111110101011111001000011010011010010
1,10,11,100.1100,10111,100010,1101,11000,1110.1111011,11101010,1111100,10000110.10011010010
Concatenating the individual bitstrings matches the bitstream
```

Which gives us the binary encoded equivalent to the integer representation of the powerset.
It's pretty obvious however that natural numbers aren't the 'natural' (as in, most amenable)
way to represent combinations in a powerset.

What the combinations of a powerset really are, are a sequence of permutations of the subsets,
specifically the permutations without descents (as mentioned above). The way to represent
permutations is as a 'bit toggle'. So now we want to encode these numbers as binary digits
in a different way: as a boolean/bit toggle of the 4 positions (but for any `n`).

Note that this is **not** simply the binary integer you get from 

- `pybtickblock --nofilecat print_combs_gen_bin_to_pos.py`

```STDOUT
[['1', '10', '11', '100'], ['1100', '10111', '100010', '1101', '11000', '1110'], ['1111011',
'11101010', '1111100', '10000110'], ['10011010010']]
⇣
1,2,3,4.12,23,34,13,24,14.123,234,124,134.1234
```

- Call these the binary integers, _𝕫𝕓_
- In this order `{1, 10, 11, 100, ...}` call them _ρ(𝕫𝕓)_

What I want to know is: given (either of the 3 equivalent representations of) the
**generation order** (_ρ_) of the permutations _π_ (of _n_ items, here `n=4`) without descents
[PWDs], how to generate _ρ_ from the lexicographic sort order of the same set of PWDs (_σ_)?

- In case that looks complex, it's really just asking: what's the relation between the two
  permutations _ρ_ and _σ_?
  - It just looks a little more complicated as they are both composed of (the same set of)
    'sub'-permutations (_π_)

It'll clarify the question somewhat to spell it out.
