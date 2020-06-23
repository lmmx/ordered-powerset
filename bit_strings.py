from bitstring import Bits, BitStream, pack
from math import ceil, log2

def bitstr_len(n):
    """
    Return the maximal length bitstring in `range(n)`, i.e. the length of the
    binary bitstring of `n-1`, which is the final term in `range(n)`.
    """
    return max(1, ceil(log2(n+1)))

def bitstream_ins(iterable=None, n=None, identical_lengths=True):
    """
    Return a BitStream representation of `iterable` by repeated insertions.

    All bitstrings are of the same length when `identical_lengths` is True,
    and will only be as long as needed (i.e. no left zero padding) if False.
    """
    if n is None:
        assert not iterable is None, ValueError("Must provide iterable or n")
        n = len(iterable)
    else:
        assert isinstance(n, int), TypeError("n must be an integer")
    l = bitstr_len(n)
    bit_range = range(n)
    bstream = BitStream()
    # You can also just do it in one string? Maybe time it?
    if identical_lengths:
        for b in bit_range:
            l = bitstr_len(b)
            insert_into_bitstream(bstream, b, l)
    else:
        for b in bit_range:
            insert_into_bitstream(bstream, b, l)
    return bstream

def insert_into_bitstream(bs, n, l):
    "Insert the integer `n` as an `l`-length bit into the bitstream `bs`"
    bs.insert(f"{l}={n}")
    return

def bitstream_pack(iterable):
    "Return a BitStream representation of `iterable` by packing."
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
