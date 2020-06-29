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
