from bitstring import Bits, BitStream, pack
from math import ceil, floor, log2 #, frexp
from more_itertools import all_equal

def bitstr_len(n):
    """
    Return the maximal length bitstring in `range(n)`, i.e. the length of the
    binary bitstring of `n-1`, which is the final term in `range(n)`.
    """
    #return max(1, ceil(log2(n+1)))
    return max(1, n.bit_length())

def bitstr_len_lencoded(n):
    """
    Return the maximal length bitstring in `range(n)`, i.e. the length of the
    binary lencoded bitstring of `n-1`, which is the final term in `range(n)`.

    Regular bitstrings encode `range(6)` as:    `{0,1,10,11,100,101}`
    whereas lencoded bitstrings encode them as: `{0,1,00,01,10,11}`

    Lencoded bitstrings produce smaller bitstreams but are not uniquely decodable
    as integers, e.g. the lencoded integers 0 and 2 are `0` and `00` which are
    numerically equal in value, but not in bitstring length: `ƒ(0)=1`, `ƒ(2)=2`
    (ƒ is the function calculated by this funcdef `⌈log₂(n+3)⌉-1`).
    """
    # return ceil(log2(n+3))-1
    return (n+2).bit_length()-1

def bitstr_lencoded_value_offset(n):
    """
    This is the minuend, subtraction from which of the (subtrahend) input value
    `n` gives the length "run" index in the lencoded bitstring range.
    
    I.e. the offset from the apparent value of the encoded integer, due to lencoding,
    which can be added to that lencoded binary value to obtain its decoded value.

    E.g. `range(6)` is lencoded as the bitstrings: `{0,1,00,01,10,11}`:
    - the 4th bitstring in the above sequence, `01`, corresponds to
      `n=3` (the 4th 0-based lencoded integer), which results in:
    - ƒ(3) = `2^(⌊log₂(3+2)⌋)-2` = `2^(⌊log₂(5)⌋)-2` = `2²-2` = `2¹` = 2
      ∴ the 4th bitstring, `01`, has readout offset of 2, which we can verify
      ∵ `n - ƒ(n) ≡ int(n, 2)` = `3 - 2 ≡ int('01', 2)` = `1 ≡ 1₁₀`
      - i.e. 1 (base 10) is the decimal integer of the bitstring '01' (base 2)
    """
    # equivalent to `2**floor(log2(n+2))-2` but bit_length is a native int method
    # see https://stackoverflow.com/a/28033134/2668831
    return 2**(bitstr_len_lencoded(n)) - 2

def bitstream_ins(iterable=None, n=None, bstream=None, fixed_length=False, lencode=False, v=False):
    """
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
    """
    assert not (lencode and fixed_length), ValueError("Can't lencode fixed length")
    if n is None:
        assert not iterable is None, ValueError("Must provide iterable or n")
        n = len(iterable)
        assert all_equal(map(type, iterable)), TypeError("iterable of mixed types")
        if n > 0:
            msg = "Not an iterable of `int`s: omit & provide `n=len(iterable)` instead"
            assert isinstance(iterable[0], int), TypeError(msg)
    else:
        assert isinstance(n, int), TypeError("n must be an integer")
        assert not n < 0, ValueError("n cannot be negative")
    if n == 0:
        # void iterator from 0-length `iterable` or `n=0` always gives empty bitstring
        return BitStream() # BitStream("").bin is BitStream().bin
    lenfunc = bitstr_len_lencoded if lencode else bitstr_len
    if fixed_length:
        if iterable is None:
            if n > 2:
                max_l = lenfunc(n-1)
            else:
                max_l = 1
        else:
            # Can't see how to check maximum value needed for max_l other than iterating
            max_val = max(iterable)
    bit_seq = range(n) if iterable is None else iterable
    if v:
        print(f"Initialising stream on {bit_seq}")
    if bstream is None:
        bstream = BitStream()
    assert isinstance(bstream, BitStream), TypeError("bstream ≠ bitstring⠶BitStream")
    if fixed_length:
        for b in bit_seq: # `range(n)` or `iterable`
            if v:
                print(f"Inserting {b} at length {max_l}")
            insert_into_bitstream(bstream, b, max_l)
    else:
        if lencode:
            if iterable is None:
                bit_length_counter = bin_readout_offset = 0 # initialise counts
                for b in bit_seq: # `range(n)`
                    if b > 1:
                        ###l2bp2 = (b+2).bit_length()-1 # l2bp2 means "log2 b plus 2"
                        l2bp2 = bitstr_len_lencoded(b)
                        if l2bp2 > bit_length_counter: # b = 2,6,14,30,...
                            bit_length_counter = l2bp2
                            bin_readout_offset = 2**bit_length_counter - 2
                        # (the rest) b = 3,4,5, 7,...,13, 15...29, 31,...
                        l = lenfunc(b) # assign l based on 'true' (decoded) value
                        # decoded value minus offset = encoded value
                        b -= bin_readout_offset # reassign rather than making
                    else: # (b < 2) are not modified by 'lencoding'
                        # fall thru without counter++ or `b -= bin_readout_offset`
                        l = lenfunc(b)
                    if v:
                        print(f"Inserting {b} at length {l}")
                    insert_into_bitstream(bstream, b, l)
            else:
                bit_length_counter = bin_readout_offset = 0 # initialise counts
                for b in bit_seq: # `range(n)`
                    if b > 1:
                        # no mantissa, int(log2(b+2)) via stackoverflow.com/a/28033134/
                        # log2(b+2)-1 gives the count of the run of `l`-length codewords
                        # or equivalently the power of the Mersenne prime max. codeword
                        # length `l`, e.g. 2^(3)-1 = 7, 7 is the max. lencoded codeword
                        # length `l=3` (i.e. in binary 7 is `111`).
                        ###l2bp2 = (b+2).bit_length()-1 # l2bp2 means "log2 b plus 2"
                        l2bp2 = bitstr_len_lencoded(b)
                        if l2bp2 > bit_length_counter: # b = 2,6,14,30,...
                            bit_length_counter = l2bp2
                            bin_readout_offset = 2**bit_length_counter - 2
                        # (the rest) b = 3,4,5, 7,...,13, 15...29, 31,...
                        l = lenfunc(b) # assign l based on 'true' (decoded) value
                        # decoded value minus offset = encoded value
                        b -= bin_readout_offset # reassign rather than making
                    else: # (b < 2) are not modified by 'lencoding'
                        # fall thru without counter++ or `b -= bin_readout_offset`
                        l = lenfunc(b)
                    if v:
                        print(f"Inserting {b} at length {l}")
                    insert_into_bitstream(bstream, b, l)
        else:
            for b in bit_seq: # `range(n)` or `iterable`
                l = lenfunc(b)
                if v:
                    print(f"Inserting {b} at length {l}")
                insert_into_bitstream(bstream, b, l)
    return bstream

def insert_into_bitstream(bs, n, l):
    "Insert the integer `n` as an `l`-length bit into the bitstream `bs`"
    bs.insert(f"{l}={n}")
    return

####### Deprecated functions: ##################################################

def bitstream_pack(iterable):
    "(Deprecated) Return a BitStream representation of `iterable` by packing."
    l = bitstr_len(iterable)
    bit_range = range(2**l)
    stream_input_str = ",".join(['='.join(map(repr, [l,b])) for b in bit_range])
    packed_stream = pack(stream_input_str)
    return packed_stream

def bitstrings_generator(iterable=None, n=None):
    """
    Return a generator of (separate) equal-length bitstrings over `range(1,n)`,
    where n is either a given integer or the length of the `iterable`.

    N.B. may be best practice to use `BitStream` instead of looping over `Bits`.
    """
    if n is None:
        assert not iterable is None, ValueError("Must provide iterable or n")
        n = len(iterable)
    else:
        assert isinstance(n, int), TypeError("n must be an integer")
    l = bitstr_len(n) # make all bitstrings identical length
    bit_range = range(2**l)
    for b in bit_range:
        bs = Bits(uint=b, length=l)
        yield bs
