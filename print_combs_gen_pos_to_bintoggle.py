from ord_pset import bit_strings

# gen = [
#     ["1", "2", "3", "4"],
#     ["12", "23", "34", "13", "24", "14"],
#     ["123", "234", "124", "134"],
#     ["1234"],
# ]
gen = [
    [ "1", "2", "3", "4", "5", "6" ],
    [ "12", "23", "34", "45", "56", "13", "24", "35",
      "46", "14", "25", "36", "15", "26", "16" ],
    [ "123", "234", "345", "456", "124", "235", "346", "134", "245", "356", "125",
      "236", "145", "256", "135", "246", "126", "156", "136", "146"  ],
    [ "1234", "2345", "3456", "1235", "2346", "1245", "2356", "1345",
      "2456", "1236", "1256", "1456", "1246", "1346", "1356" ],
    [ "12345", "23456", "12346", "12356", "12456", "13456" ],
    [ "123456" ],
]
print(gen, end="\n⇣\n")

bs = bit_strings.BitStream()
split_bs = []
individual_bit_levels = []
max_bitlen = max(map(lambda x: max(map(len, x)), gen))  # 4

for g in gen:
    individual_bitstrings = []
    for v in g:
        toggle = [False] * max_bitlen
        for p in v:
            # equivalently: use pos as max_bitlen - int(p) then reverse
            pos = int(p) - 1
            toggle[pos] = True
        b = bit_strings.Bits(toggle)
        bs.insert(b)
        individual_bitstrings.append(b.bin)
    jb = ",".join(individual_bitstrings)
    individual_bit_levels.append(jb)

print(bs.bin)
print(".".join(individual_bit_levels))

jib = "".join(individual_bit_levels).replace(",", "")
assert jib == bs.bin, ValueError(
    "The individual bitstrings don't concatenate into the bitstream"
)
print("Concatenating the individual bitstrings matches the bitstream")
