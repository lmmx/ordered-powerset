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

- Call these the 'binary integers', _𝕫𝕓_ (top line) and call their 'integer'
  form _𝕫_
- In this order call them _ρ(𝕫)_ and _ρ(𝕫𝕓)_
- Observe that whichever form it's in, the _integer values_ (note: not the permutations)
  are descending at some points: i.e. if you were to compare them to a lexicographically sorted list
  of the same integers you would say that there is a 'descent'
  - e.g. _ρ(𝕫)_ contains `{34,13}` whereas a lexicographically sorted list would not be in this order
    (in fact there would be intervening values: the sequence would be `{13, ..., 34}`)

What I want to know is: given (either of the 3 equivalent representations of) the
**generation order** (_ρ_) of the permutations _π_ (of _n_ items, here `n=4`) without descents
[PWDs], how to generate _ρ_ from the lexicographic sort order (_σ_) of the same set of PWDs _π_?

- In case that looks complex, it's really just asking: what's the relation between the two
  permutations _ρ_ and _σ_?
  - It just looks a little more complicated as they are both composed of (the same set of)
    'sub'-permutations (_π_), which we are representing as integers when we write _𝕫_ (e.g. `34`).

It'll clarify the question somewhat to spell this out in more detail.

Notice that I mentioned **3 forms** of the permutation order we are calling rho: but so far I only
introduced _ρ(𝕫)_ and _ρ(𝕫𝕓)_.

The third form is _ρ(𝕓)_, which is the binary 'toggle' and is the far more 'natural' (again, as in
amenable) way to represent these PWDs: if the PWD contains an item, we toggle it.

The standard way I learnt to write binary (and textbooks vary on this convention) is the one
that makes them look most like a polynomial, with coefficients in descending order left to right.

For `n=4`, this means for a binary codeword of length 4,

> 𝕓₄ = 𝔹₃𝔹₂𝔹₁𝔹₀

The 'bit toggle' generation order (henceforth _ρ(𝕓)_) can be derived from the integer generation
order _ρ(𝕫)_ as a polynomial (and vice versa for that matter).

This is visible, but recall that what we want to obtain is something like a Gray code (or some other
Reed-Muller code), which will allow us to generate the combinations from a single iterator,
and therefore allow us to keep fewer integers in memory (as explained already).

Recall the module `string_powerset.py` which takes a quoted string of any set of elements and
returns their combinations, which we earlier used to obtain all combinations of '1234'. We can
use the function it imports `generate_powerset` from the `pset_partitions` module, or
be lazy and just interactively jump into the shell after running `string_powerset` where we
will have access to the variable `ps`, as the source code shows:

```py
from pset_partitions import generate_powerset, string_handler
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("items_str", action="append", help="A string to" +
    "be split as multiple items, or multiple space-separated strings, " +
    "representing the set of items whose powerset is to be determined")
parser.add_argument("-q", "--quiet", dest="verbose", action="store_false")
args = parser.parse_args()

items = list(args.items_str)

if len(items) == 1:
    items = list(items[0])

ps = generate_powerset(items, subset_handler=string_handler, verbose=args.verbose)
```

So running `python -i string_powerset.py '1234'`, we can copy the array with which
to get a look at our final generation order, _ρ(𝕓)_:

```py
1, 2, 3, 4

12, 23, 34
13, 24
14

123, 234
124
134

1234
>>> ps
{0: ['', '1', '2', '3', '4'], 1: ['12', '23', '34', '13', '24', '14'], 2: ['123', '234', '124',
'134'], 3: ['1234']}
>>> list(ps.values())
[['', '1', '2', '3', '4'], ['12', '23', '34', '13', '24', '14'], ['123', '234', '124', '134'],
['1234']]
```

Again note that we will discard the empty string as a special case, and use these in the variable
`gen` to get the binary toggle bitstrings

- `pybtickblock --nofilecat print_combs_gen_pos_to_bintoggle.py`

```STDOUT
[['1', '2', '3', '4'], ['12', '23', '34', '13', '24', '14'], ['123', '234', '124', '134'], ['1234']]
⇣
100001000010000111000110001110100101100111100111110110111111
1000,0100,0010,0001.1100,0110,0011,1010,0101,1001.1110,0111,1101,1011.1111
Concatenating the individual bitstrings matches the bitstream
```

So now it's quite clear (I'd hope) that viewing the sequence as binary makes the earlier
distance interpretation very apparent.

We can first see the progression in terms of the sum of the binary digits, i.e. the count of nonzero
bits (as delimited by `.` in the bitstream above):

- Sum 1: `1000,0100,0010,0001`
- Sum 2: `1100,0110,0011,1010,0101,1001`
- Sum 3: `1110,0111,1101,1011`
- Sum 4: `1111`

But further than this, we can see the distances between nonzero bits:

- Sum 1:
  - d = `(0)`: `1000,0100,0010,0001`
- Sum 2:
  - d = `(1)`: `1100,0110,0011`
  - d = `(2)`: `1010,0101`
  - d = `(3)`: `1001`
- Sum 3:
  - d = `(1,1)`: `1110,0111`
  - d = `(1,2)`: `1101`
  - d = `(2,1)`: `1011` **!!!**
- Sum 4:
  - d = `(1,1,1)`: `1111`

There's one interesting line here – the non-unit distance sum-3 distances are sorted as `{(1,2), (2,1)}`!

This means that we know from this example alone (from this single pair of distance tuples `(1,2)`
and `(2,1)`) that not only are the sums and total distance ascending for this sequence _ρ(𝕓)_,
we can actually see these permutations of `d` are in ascending order of distances when their sum is the same.

To put this another way, we don't pay any attention to the fact that these values appear to be "anti-lexicographically
sorted" (lexicographically reverse order), i.e. the binary strings when the sum of distances between
nonzero bits is the same seem to 'decrease'. Lexicographically, `1011` looks like it should be less
than `1101`, as surely `134` < `124`, no?

Recall however that we're not truly looking at binary integers here, but binary toggles: the
("lossless") binary for 124 is `1111100` [7 digits] and 134 is `10000110` [8 digits].

But these aren't what we're looking at, and this is why it's actually unhelpful to keep referring to
what are actually permutations (PWDs, _π_) as if they were ordinal numbers (natural numbers).

Having said that, perhaps we could consider making the distance counts binary too:

- Sum 1:
  - d = `(0)`: `1000,0100,0010,0001`
- Sum 2:
  - d = `(1)`: `1100,0110,0011`
  - d = `(10)`: `1010,0101`
  - d = `(11)`: `1001`
- Sum 3:
  - d = `(1,1)`: `1110,0111`
  - d = `(1,10)`: `1101`
  - d = `(10,1)`: `1011` **!!!**
- Sum 4:
  - d = `(1,1,1)`: `1111`

After doing that, if we then 'merge' these binary distance counts into a single label...

- Sum 1:
  - d = `(0)`: `1000,0100,0010,0001`
- Sum 2:
  - d = `(1)`: `1100,0110,0011`
  - d = `(10)`: `1010,0101`
  - d = `(11)`: `1001`
- Sum 3:
  - d = `(11)`: `1110,0111`
  - d = `(110)`: `1101`
  - d = `(101)`: `1011` **!!!**
- Sum 4:
  - d = `(111)`: `1111`

Now what we observe are two things:

- Repetitions:
  - d = `(11)`: `1001`
  - d = `(11)`: `1110,0111`
- Descending order binary integers:
  - d = `(110)`: `1101`
  - d = `(101)`: `1011` **!!!**

For the repetitions, since we know that they can't have been formed from the same binary distance tuples
(since each of these occurs only once in the sequence), then they must have been formed by the
merging of smaller binary numbers (and thus we can always rely on any repetitions being 'greater
than' the earlier one, and we know that if we've seen it before then it must have been merged from a
greater number of distances than the preceding).

- E.g. `11` was a sum 2 distance tuple which was followed by something which appears to be another
  `11`, but since this is impossible then it can only be `1,1`. So in fact, we don't even need to
  keep track of the length (i.e. we can omit the lines which count the sum of the nonzero binary digits).
  - Let's drop that `d` while we're at it

**Abridged generation line format**

```
0:    1000,0100,0010,0001
1:    1100,0110,0011
10:   1010,0101
11:   1001
11:   1110,0111
110:  1101
101:  1011
111:  1111
```

Next, the descending order binary integers. All that can be said of them is that they only occur within
the same length

- `(110)`: `1101`
- `(101)`: `1011` **!!!**

or

- `(110)`: `1101`
- `(101)`: `1011` **!!!**

So really then, what we have so far thought of as `n`-length sequences can really be
characterised in terms of their distances  which are binary bitstrings of lengths in the range
`[1,n)` (i.e. `[1,n-1]` but it's neater to write in standard range notation and matches Python).

Lastly, we should also note that on the lines as we've written them out, the binary numbers are all
actually in descending order. This is equivalent to stating the positions should be "filled" in
ascending order, however since we'll be working in binary let's set our convention as "descending
[binary] order" for binary permutations of identical "distance tuple" (i.e. not across lines which
share the distance bitstring, since we know they 'really' came from different distance tuples).

In terms of forming a unique sequence then, we will need to distinguish these equivalent generating
distance tuples which we have now "merged" into a single bitstring and as such "repeat" in some way.

The way to do so is to left-pad the larger ones with zeroes: in standard binary this is the same
number, but **in our "lencoded" bitstrings these are distinct values**.

Recall how we counted with them (here for the six values `{0,1,2,3,4,5,6}`):

```
Lossless:      011011100101        =  {0,1,10,11,100,101}
Lencoded:      0100011011          =  {0,1,00,01,10,11}
Fixed length:  000001010011100101  =  {000,001,010,011,100,101}
```

So far though, I only obtained the lencoded bitstrings through a `range` (sequence) object in
Python, not for arbitrary values. This is unhelpful for determining the values of `11` and `011`
right now: however it suggests that **if we can determine the maximum distance-tuple (mDT) then we can
also determine its merged bitstring (mDTMB) and the range of lencoded values up to the MDMB
will give a single iterator.**

This is great, as it'll mean that we can derive a Gray code (a unit Hamming distance code) whereas
so far the codes we've seen have been about non-monotonic distances

E.g. on the example above (before we converted the distance tuples to binary) we had:

- Sum 2:
  - ...
  - d = `(3)`: `1001`
- Sum 3:
  - d = `(1,1)`: `1110,0111`

...in which the distance-tuple `(3)` decreased to `(1,1)` and we had to resort to saying that
we were ordering them according to the length of their tuple not the values inside them, which
of course works but is unsatisfying in terms of number progressions.

Note that this was 'fixed' when we switched to DTMBs (Distance Tuple Merged Bitstrings), and
here I'll omit the switch from sum-2 to sum-3 for brevity:

- d = `(11)`: `1001`
- d = `(1,1)`: `1110,0111`
---
- d = `(11)`: `1001`
- d = `(11)`: `1110,0111`

...but the 'fix' came at the cost of "repeating" identical [DTMB] bitstrings, `11` and `11`.

If we now go through and lencode these repeated DTMBs so that they're the same length as the sums, then
we will actually justify our earlier decision to throw away the sum values (which recall, were not
for the DTMBs but the binary bitstrings length `n=4` on the right of each DTMB).

- Sum 1:
  - d = `(0)`: `1000,0100,0010,0001`
- Sum 2:
  - d = `(1)`: `1100,0110,0011`
  - d = `(10)`: `1010,0101`
  - d = `(11)`: `1001`
- Sum 3:
  - d = `(011)`: `1110,0111`
  - d = `(110)`: `1101`
  - d = `(101)`: `1011` **!!!**
- Sum 4:
  - d = `(111)`: `1111`

Note that we have an ambiguity: we don't seem to need to lencode the tuple `(1)` as it's not a
repeat. So this rule does not apply to all values: in fact it only doesn't apply to the first
DTMB in the case of `n=4`. We'll look at a higher `n` next to check if this holds.

**Somewhat De-Abridged generation line format**

```
0:    1000,0100,0010,0001
1:    1100,0110,0011
10:   1010,0101
11:   1001
011:  1110,0111
110:  1101
101:  1011
111:  1111
```

Now that we've established a unique binary sequence of distance labels (we'll simply call them
_d_ again now that we now they're Distance Tuple Merged Bitstrings, DTMBs), we can decode them
as lencoded numbers.

If we go ahead and load `python -im ord_pset` and recall `help(bit_strings.bitstream_ins)`:

```py
bitstream_ins(iterable=None, n=None, bstream=None, fixed_length=False, lencode=False, v=False)
    Return a BitStream representation of `iterable` by repeated insertions.
    `iterable` should be an iterable of integers, such as from `range(n)`.
    
      `bitstream_ins(range(0)).bin` --> `""`
      `bitstream_ins(range(1)).bin` --> `"0"`
      `bitstream_ins(range(2)).bin` --> `"01"`
    
    If `iterable` is not provided (or provided as `None`), `n` must be instead,
    and `iterable` will be created as `range(n)`. Providing both `iterable` and
    `n` will raise a `ValueError`.
    
    All bitstrings are of the same length when `fixed_length` is True, or
    else will be only as long as needed (i.e. no left zero padding) if False
    (default: False).
    
    If `fixed_length` is False and `lencode` is True, the bitstream will be
    further compressed by encoding the same value at different lengths
    
    `range(6)` bitstrings if `fixed_length`: `{0,1,10,11,100,101}`
     --> bitstream: '0110111000101', length = 13
    `range(6)` bitstrings if `fixed_length` & `lencode`: `{0,1,00,01,10,11}`
     --> bitstream: '0100011011', length = 10
    
    Must provide a uniquely decodable bitstream: cannot reuse codewords for different
    symbols ∴ `lencode` is forbidden unless `fixed_length` is False.
    
    Print progress information on the range being created and individual insertions
    (integer, length) if the verbosity parameter `v` is True.
```

We now satisfy the following requirement:

> **Must provide a uniquely decodable bitstream: cannot reuse codewords** for different
> symbols ∴ `lencode` is forbidden unless `fixed_length` is False.

```py
max_n = 8
for n in range(max_n):
    print(bit_strings.bitstream_ins(n=n, lencode=True).bin)
```
⇣
```STDOUT
0
01
0100
010001
01000110
0100011011
0100011011000
```

Does this match our bitstream?

- These are the row labels before the colon in the _"Somewhat De-Abridged generation line format"_
  above, placed in a Python list

```py
gen_bitstrings = ['0', '1', '10', '11', '011', '110', '101', '111']
print("".join(gen_bitstrings))
```
⇣
```STDOUT
011011011110101111
```

- Lencoded bitstream up to `n=8` terms:
  - `0100011011000`
- Our generating sequence bitstream:
  - `011011011110101111`

No, clearly not: in fact the sequence we generate from `bitstream_ins(n=8, lencode=True)`
is much more compact. But surely we have some terms from it: let's quickly check what those are.

```py
max_n = 8
seen_bitlen_count = 0
for n in range(max_n):
    bs = bit_strings.bitstream_ins(n=n, lencode=True).bin
    new_bitstring = bs[seen_bitlen_count:]
    seen_bitlen_count += len(new_bitstring)
    print(new_bitstring, f"({n})")
```
⇣
```STDOUT
 (0)
0 (1)
1 (2)
00 (3)
01 (4)
10 (5)
11 (6)
000 (7)
```

- Notice the empty string is our 'zero': we will use this but for now we are counting with
  these bitstrings so we will skip this and consider our ranges starting at `n=1`.

Now compare these 7 non-empty bitstrings to our sequence:

```py
gen_bitstrings = ['0', '1', '10', '11', '011', '110', '101', '111']
print("\n".join(f"{b} ({i+1})" for i, b in enumerate(gen_bitstrings)))
```
⇣
```STDOUT
0 (1)
1 (2)
10 (3)
11 (4)
011 (5)
110 (6)
101 (7)
111 (8)
```

The first difference is that our generation sequence cannot contain runs of zeroes
after the first bitstring `0`

- else we would see `00` after `1` (not `10`) and `000` after `11` (not `011`).

Again let's not rewrite any code yet, and just add 2 to the range we iterate over
(to account for the two bitstrings with runs of multiple zeroes (and nothing else)

- i.e. we just found that we need to skip the two values `00` and `000` so we need to
  make up for their loss by increasing the range of values we take `n` up to

```py
max_n = 8
zero_run_offset = 2
zero_offset_count = 0
seen_bitlen_count = 0
for n in range(1, max_n + zero_run_offset):
    bs = bit_strings.bitstream_ins(n=n, lencode=True).bin
    new_bitstring = bs[seen_bitlen_count:]
    seen_bitlen_count += len(new_bitstring)
    if len(new_bitstring) > 1 and '1' not in new_bitstring:
        zero_offset_count += 1
        continue
    print(new_bitstring, f"({n - zero_offset_count})")
```
⇣
```STDOUT
0 (1)
1 (2)
01 (3)
10 (4)
11 (5)
001 (6)
010 (7)
```

The next difference is that we shouldn't have:
- `01 (3)` we should skip it to get `10 (3)`
- `001 (6)` we should skip it, and skip `010` then take `011 (6)`

...and if we take these out in our loop...

```py
max_n = 8
zero_run_offset = 2
zero_offset_count = 0
seen_bitlen_count = 0
for n in range(1, max_n + zero_run_offset):
    bs = bit_strings.bitstream_ins(n=n, lencode=True).bin
    new_bitstring = bs[seen_bitlen_count:]
    seen_bitlen_count += len(new_bitstring)
    if len(new_bitstring) > 1 and '1' not in new_bitstring:
        zero_offset_count += 1
        continue
    print(new_bitstring, f"({n - zero_offset_count})")
```
⇣
```STDOUT
0 (1)
1 (2)
10 (3)
11 (4)
001 (5)
011 (6)
100 (7)
```

Is still not right compared to the above abridged

> 0:    ... (1)
> 1:    ... (2)
> 10:   ... (3)
> 11:   ... (4)
> 011:  ... (5)
> 110:  ... (6)
> 101:  ... (7)
> 111:  ... (8)

...we might get to `110` by adding new rules to skip values in the sequence, but since there's then
a 'decrement' from `110` to `101`, it's pretty clear that **this sequence
is not 'lencoded'**. To say more precisely what this sequence is, let's
restate what 'lencoded' really means.

Recall we earlier mentioned that we could consider the lencoded binary integers as:

> the union of the sets of codewords `⋃ { {0,1}ⁱ }` for all `i ∊ range(n)`

'Lencoded' binary is a way of counting in binary that conjoins (or concatenates)
successive fixed length codes, and **must** use every codeword within those codes.

> `⋃ { {0,1}ⁱ }`

`{0,1}⁺⁺` should therefore really have an indicator of its maximum codeword length,
_n_, perhaps written as `{0,1}⁺⁺ⁿ` as a working notation, because our earlier
notation was ambiguous: if we wanted to go up to _n_ then we'd need to set `i = n+1`
(as the `range` is zero-based, so `range(n)` only gives you `{0,...,n-1}`).

When we obtained the output of `bitstream_ins(n=8, lencoded=True)`, the successive
fixed length codes which made it up were the length 0, length 1, length 2, and
length 3 codes. The largest codeword length was 3, so we'll call it `{0,1}⁺⁺³`.

In our new notation:

`{0,1}⁺⁺ⁿ` = `⋃ { {0,1}ⁱ }` for all `i ∊ range(1, n+1)`

- ...or `range(0,n+1)` if we want to include the empty bitstring as the singleton element of the
  zero-length codewords: but for now our convention will omit this and we will work with positive
  integer length bitstrings.

So to return to our attempt to recreate the 7 bitstrings from `0` to `111`, with a maximum length of
3 and therefore `n=3`, the new notation is to write the lencoded binary sequence as:

`{0,1}⁺⁺³`

- = `⋃ { {0,1}ⁱ }` for all `i ∊ range(1, n+1)`
- = `⋃ { {0,1}¹, {0,1}², {0,1}³ }`
- = `⋃ { {0,1}, {00,...,11}, {000,...,111} }`
- = `⋃ { {0,1}, {00,...,11}, {000,...,111} }`

so it's the union (concatenation) of:

- (`{0,1}⁰` but we're not considering this by convention)
- `{0,1}¹`
- `{0,1}²`
- `{0,1}³`

Another way to look at the sequence is to write its "complement" (flipping every bit) alongside, on
the right of the previous two columns:

```
0 (1) 1
1 (2) 0
01 (3) 10
10 (4) 01
11 (5) 00
001 (6) 110
010 (7) 101
```

When we do so, it appears that maybe we should actually consider it as 'counting down', and the relation between lines as something
to do with flipping an individual bit. So on the 1st-2nd rows we flip the first bit, then to go to
the 3rd row we can't flip `0` as it'd regress to the 1st row, so we add another bit (i.e. advance to
the next codeword length)

- We don't start at `11` because we need to flip a single bit
  - so by this logic, the bit we add is at the end of the word (`0` gets flipped to `1` and then
    right-padded with a `0` to give `10`)
- We flip both as to flip just one would give us `00` or `11`
  - let's say that there is a rule that the new value must be a smaller binary number, so we can't
    choose `11` as it's a larger binary number than `10`
  - let's say that there is a rule that the new value must have a different value to the preceding
    value, so we can't choose `00` as that has the same 'readout' value (i.e. sum) of zero as the
    preceding line (`0` at line 2)

Perhaps there is some rule we can define in this way. We should look for this with the larger set of
bitstrings for `n=6`.

To gauge the pattern more clearly, let's build back up to 6 items (as at the start with `abcdef`):

```sh
python string_powerset.py 123456 | sed -e 's/^$/./g' | tr '\n' ',' | sed 's/,.,/./g' | tr -d ' '
```
⇣
```STDOUT
1,2,3,4,5,6.12,23,34,45,56,13,24,35,46,14,25,36,15,26,16.123,234,345,456,124,235,346,134,245,356,125,236,145,256,135,246,126,156,136,146.1234,2345,3456,1235,2346,1245,2356,1345,2456,1236,1256,1456,1246,1346,1356.12345,23456,12346,12356,12456,13456.123456,
```

...this gets too long, let's leave in the empty lines between the bit lengths

```sh
python string_powerset.py 123456 | sed -e 's/^$/./g' | tr '\n' ',' | sed 's/,.,/./g' | tr -d ' ' | tr '.' '\n'
```
⇣
```STDOUT
1,2,3,4,5,6
12,23,34,45,56,13,24,35,46,14,25,36,15,26,16
123,234,345,456,124,235,346,134,245,356,125,236,145,256,135,246,126,156,136,146
1234,2345,3456,1235,2346,1245,2356,1345,2456,1236,1256,1456,1246,1346,1356
12345,23456,12346,12356,12456,13456
123456,
```

With some minimal editing, the script to generate the binary toggle for `n=4` now gives us the
binary toggles for these numbers:

- `pybtickblock --nofilecat print_combs_gen_pos_to_bintoggle.py`

```STDOUT
[['1', '2', '3', '4', '5', '6'], ['12', '23', '34', '45', '56', '13', '24', '35', '46', '14', '25',
'36', '15', '26', '16'], ['123', '234', '345', '456', '124', '235', '346', '134', '245', '356',
'125', '236', '145', '256', '135', '246', '126', '156', '136', '146'], ['1234', '2345', '3456',
'1235', '2346', '1245', '2356', '1345', '2456', '1236', '1256', '1456', '1246', '1346', '1356'],
['12345', '23456', '12346', '12356', '12456', '13456'], ['123456']]
⇣
100000010000001000000100000010000001110000011000001100000110000011101000010100001010000101100100010010001001100010010001100001111000011100001110000111110100011010001101101100010110001011110010011001100110010011101010010101110001100011101001100101111100011110001111111010011101110110011011101110010111111001110011100111110101101101101011111110011111111101111011110111101111111111
100000,010000,001000,000100,000010,000001.110000,011000,001100,000110,000011,101000,010100,001010,000101,100100,010010,001001,100010,010001,100001.111000,011100,001110,000111,110100,011010,001101,101100,010110,001011,110010,011001,100110,010011,101010,010101,110001,100011,101001,100101.111100,011110,001111,111010,011101,110110,011011,101110,010111,111001,110011,100111,110101,101101,101011.111110,011111,111101,111011,110111,101111.111111
Concatenating the individual bitstrings matches the bitstream
```

We want to print that out a bit more nicely:

- `python print_combs_gen_pos_to_bintoggle.py | grep "\." | tr '.' '\n' | sed 's/,/, /g' | btickblock - --stdout`

```STDOUT
100000, 010000, 001000, 000100, 000010, 000001
110000, 011000, 001100, 000110, 000011, 101000, 010100, 001010, 000101, 100100, 010010, 001001, 100010, 010001, 100001
111000, 011100, 001110, 000111, 110100, 011010, 001101, 101100, 010110, 001011, 110010, 011001, 100110, 010011, 101010, 010101, 110001, 100011, 101001, 100101
111100, 011110, 001111, 111010, 011101, 110110, 011011, 101110, 010111, 111001, 110011, 100111, 110101, 101101, 101011
111110, 011111, 111101, 111011, 110111, 101111
111111
```

- There's something quite strange about this sequence: specifically with the first term of each
  line. There's a run of zeroes that pad out the right hand side of the significant digit (the digit
  one) in `100000`, and these zeroes steadily fill left to right until all are `1`.
- This is more reminiscent of a descent than an ascent: in a descent the significant digits are
  whittled away from the left leaving the lower values on the right.

If we take the complement (as suggested just above) then this is exactly what we get.

- `python print_combs_gen_pos_to_bintoggle.py | grep "\." | tr '.' '\n' | sed 's/,/, /g' | tr '01' '10' | btickblock - --stdout`

```STDOUT
011111, 101111, 110111, 111011, 111101, 111110
001111, 100111, 110011, 111001, 111100, 010111, 101011, 110101, 111010, 011011, 101101, 110110, 011101, 101110, 011110
000111, 100011, 110001, 111000, 001011, 100101, 110010, 010011, 101001, 110100, 001101, 100110, 011001, 101100, 010101, 101010, 001110, 011100, 010110, 011010
000011, 100001, 110000, 000101, 100010, 001001, 100100, 010001, 101000, 000110, 001100, 011000, 001010, 010010, 010100
000001, 100000, 000010, 000100, 001000, 010000
000000
```

This looks much more natural!

Next we should compare these binary values to the binary codewords obtained as the complement of the
lencoded integers (which will be used as if they were the lencoded integers, i.e. they count as
the value of their complement still).

This is a mouthful: let's call the binary codewords obtained as the complement of the lencoded
integers the "antilencoded integers", and where we symbolised the lencoded integers by

> `{0,1}⁺⁺ⁿ` = `⋃ { {0,1}ⁱ }` for all `i ∊ range(1, n+1)`

Let's symbolise the antilencoded integers by

`{1,0}ⁿ⁻⁻` = `⋃ { {1,0}ⁱ }` for all `i ∊ range(n, 0)`

The awkward `+1` has dropped out of the range (though if we want to include the empty subset
trivial combination then this time we need to change it to `range(n, -1)`).

So to get an idea of these, let's reuse the list above of the first few antilencoded integers

```
0 (1) 1
1 (2) 0
01 (3) 10
10 (4) 01
11 (5) 00
001 (6) 110
010 (7) 101
```

...but let's continue them later.

To return to our distance tuples encoded in binary, arranged by sum (of the 4-length bitstrings
placed to the right of the distance tuples):

- Sum 1:
  - d = `(0)`: `1000,0100,0010,0001`
- Sum 2:
  - d = `(1)`: `1100,0110,0011`
  - d = `(10)`: `1010,0101`
  - d = `(11)`: `1001`
- Sum 3:
  - d = `(1,1)`: `1110,0111`
  - d = `(1,10)`: `1101`
  - d = `(10,1)`: `1011` **!!!**
- Sum 4:
  - d = `(1,1,1)`: `1111`


---

A change of tack: if we write out the sequence of subsets (the powerset of all combinations)
as above, but rather than any of the previous representations, we let the 'present' items
be represented by a sequence of their indices in ascending order, followed by a descending sequence
(modulo n) of the indices of the remaining items (i.e. the absent items), then we get a
representation of the powerset as a sequence of permutations from the 'descent permutation'
to the 'ascent permutation' (for n=6 this is from 654321 to 123456).

We can represent the transition from the initial 'descent permutation' to any of the first 6
by a cyclical shift (a rotation) of the descending subpermutation, and this is clearer if
written with a vertical bar separating the ascending subsequence on the left (representing
the present items' indices) from the descending subsequence on the right (representing the
absent items' indices):

To recap, the first few are:

```
0: 
1: 1
2: 2
3: 3
4: 4
5: 5
6: 6
...
```

which become the following as permutations:

```
0: 654321
1: 1|65432
2: 2|16543
3: 3|21654
4: 4|32165
5: 5|43216
6: 6|54321
...
```

You could write the `0` permutation with a vertical bar but it doesn't seem right to me,
as there's nothing on the left to separate it from.

The `0` permutation (i.e. the "descent permutation") is the "seed" or "initial" or "base"
permutation from which every other permutation (representing the powerset, i.e. every other
subset including the full or "input set" or "identity set") is reached.

This makes intuitive sense as the empty set is indeed the only way to 'reach' the rest of the
subsets by adding other items from the input set, and to speak of "a sequence of rotations"
to build up each subset equates to "a sequence of individual set element additions".

One of the nice things about this representation is that the language of cyclical shifts
reproduces in a single statistic (the sequence of shifts) both the offset and the inter-index
distance, and it's clear how to 'reach' subsequent permutations by their composite permutations.

What I mean by this is perhaps best illustrated by a simple example: for the six letters "abcdef",
the word "bef" is represented by the indices `256`, and as a permutation by:

```
35: 256|431
```

...where the `431` descending subpermutation indicates the letters `{d,c,a}` are not in the word
"bef".

The sequence of shifts to reach the above permutation are:

```
   2°     3°      1°
0 ---> 2 ---> 17 ---> 35
```

where `2° ---> 3° ---> 1°` means "double, triple, single" and refers to the number of positions
by which the individual rotations shift the descending subsequence (a.k.a. descending
subpermutation) between each permutation (starting at `0`, then double-shifted to `2`, then
triple-shifted to `17`, then single-shifted to `35`).

That 'path' of permutations written out in full is:

```
0:  654321
            (2°)
2:  2|16543
            (3°)
17: 25|4316
            (1°)
35: 256|431
```

- Notice that you can 'read' a `i°` shift as "take the `i`'th value from the rightmost end and
  place it on the right end of the ascending subpermutation before the `|`.

Now to see the 'nice' aspect of this representation, notice that the sequence `2°,3°,1°` contains
first the number `2` (the 'offset' of the letter "b" which starts the word "bef") and then
the following numbers `3,1` are the inter-letter distances between `{ {b,e}, {e,f} }`.

In other words, this representation makes it 'simpler' to track these two distinct features,
and we can think of them as 'really' just being the relation of any given subset to the
'seed' permutation of the input set. So it makes it easier to think about inputs and outputs.

One thing that enumerating this helped me to do was to consider the problem of counting:

- the number of distinct partitions (such as `3,1`, the inter-index distances) which are
  the same for words like "ade" and "bef"
- the number of times each distinct partition appears (the partition `3,1` appears twice
  for `n=6` items: "ade" and "bef").

This requires two combinatorial tools:

- [integer partitions](https://en.wikipedia.org/wiki/Partition_(number_theory))
  - implemented very nicely in
    [Sage](https://doc.sagemath.org/html/en/reference/combinat/sage/combinat/partition.html#sage.combinat.partition.Partitions)
- the [multinomial coefficient](https://en.wikipedia.org/wiki/Multinomial_theorem#Multinomial_coefficients)
  as we want to know the number of permutations of a multiset
  - see:
    [`sage.arith.misc.multinomial`](https://doc.sagemath.org/html/en/reference/rings_standard/sage/arith/misc.html#sage.arith.misc.multinomial)

See code at [`sage/partition_counts.py`](partitions/sage_partitions.py)).

From this, we can get the correct sequence of partitions:

- Sage: `c = comb_partitions(6)`

```STDOUT
r: r_partitions
1: [[]]
2: [[1], [2], [3], [4], [5]]
3: [[1, 1], [2, 1], [3, 1], [2, 2], [4, 1], [3, 2]]
4: [[1, 1, 1], [2, 1, 1], [3, 1, 1], [2, 2, 1]]
5: [[1, 1, 1, 1], [2, 1, 1, 1]]
6: [[1, 1, 1, 1, 1]]
```

This correctly shows the partitions for `n=6, r=3` are:

- `[1, 1], [2, 1], [3, 1], [2, 2], [4, 1], [3, 2]`

and what's more, we can obtain the multinomial coefficient for each of
these partitions, taking the counts of each partition as a multiset
(e.g. the partition of `5` as `3,1,1` has counts of `1,2` (because there
is one 3 and two 1s).

- Sage: `cc = comb_partition_multinom_coeffs(6)`

```STDOUT
r: r_partition_multinom_coeffs
1: []
2: [1, 1, 1, 1, 1]
3: [1, 2, 2, 1, 2, 2]
4: [1, 3, 3, 3]
5: [1, 4]
6: [1]
```

What this shows is that the same partitions for `n=6, r=3`:

- `[1, 1], [2, 1], [3, 1], [2, 2], [4, 1], [3, 2]`

...have this many distinct rearrangements, respectively:

- `1, 2, 2, 1, 2, 2`

...which if you look at the lists, it simply means that those partitions
which are multisets of only one integer (e.g. `1,1`) will have one rearrangement,
and those which are multisets of two integers (e.g. `2,1`) will have two rearrangements
(namely one ascending and one descending arrangement).

- This will obviously not be so simple for higher values of `r`, but let's focus only on
  `n=6, r=3` to introduce the ideas.

Having established the expected number of rearrangements for the partitions, we should
compare that to the actual number of sequences we see.

The counts for `[1, 1], [2, 1], [3, 1], [2, 2], [4, 1], [3, 2]` are:

- `4,6,4,2,2,2`

These counts form a partition of 20, which is of course the binomial coefficient (6,3).

Dividing these counts by the number of rearrangements of the partitions they count, gives

- `4,3,2,2,1,1`

This sequence is a partition of 13, so the question to answer is: how do we form this
partition of 13 from only the parameters `n=6, r=3`?

- The answer is it's the difference of `n` and the sum of each partition

This means we just need to take the product of the (difference of `n` and the sum of
each partition) × (multinomial coefficient for each partition)

- This is easier to spot if you write all the sequences out on paper.

To take an example, the first partition is `[1,1]`, the sum of which is 2:

- `n=6`, so `6-2=4`, and the multinomial coeff. of `1,1` is `1` so `4×1=4`

Similarly:

- `6-(2+1)=3` so the product with the multinomial coeff (2) = `3×2=6`
- `6-(3+1)=2` so the product with the multinomial coeff (2) = `2×2=4`
- `6-(2+2)=2` so the product with the multinomial coeff (1) = `2×1=2`
- `6-(4+1)=1` so the product with the multinomial coeff (2) = `1×2=2`
- `6-(3+2)=1` so the product with the multinomial coeff (2) = `1×2=2`

..._et voilà_ we have successfully recovered the sequence `4,6,4,2,2,2` which we observed
when counting the partitions, which means we can now count the partitions for any `(r,n)`
and therefore generate any powerset sequence!

- Sage: `c = comb_partitions(6)`

```STDOUT
r: r_partitions
1: [[]]
2: [[1], [2], [3], [4], [5]]
3: [[1, 1], [2, 1], [3, 1], [2, 2], [4, 1], [3, 2]]
4: [[1, 1, 1], [2, 1, 1], [3, 1, 1], [2, 2, 1]]
5: [[1, 1, 1, 1], [2, 1, 1, 1]]
6: [[1, 1, 1, 1, 1]]
```

- Sage: `cc = comb_partition_counts(6)`

```STDOUT
r: r_partition_counts
1: []
2: [(5, 1), (4, 1), (3, 1), (2, 1), (1, 1)]
3: [(4, 1), (3, 2), (2, 2), (2, 1), (1, 2), (1, 2)]
4: [(3, 1), (2, 3), (1, 3), (1, 3)]
5: [(2, 1), (1, 4)]
6: [(1, 1)]
```

This can be read by taking the partition from the `comb_partitions` output
and then matching to the same row/list position in the output of `comb_partition_counts`,
which is a tuple of:

- number of times each rearrangement of that partition is seen
- number of rearrangements of that partition

E.g. for `n=6, r=5`:

```
5: [[1, 1, 1, 1], [2, 1, 1, 1]]
5: [(2, 1), (1, 4)]
```

means:

- `1,1,1,1` twice, in one rearrangement
- `2,1,1,1` once, in four rearrangements

A convenience function can do this operation for a given `(n,r)`.

---

Don't forget TODO items plz!

(Go back and do TODO code a few paragraphs above plz)

