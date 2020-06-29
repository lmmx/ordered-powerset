from ord_pset import bit_strings

gen = [
    ["1", "10", "11", "100"],
    ["1100", "10111", "100010", "1101", "11000", "1110"],
    ["1111011", "11101010", "1111100", "10000110"],
    ["10011010010"],
]
print(gen, end="\n⇣\n")

individual_z_levels = []

for g in gen:
    individual_ints = []
    for zb in g:
        b = bit_strings.Bits(f"0b{zb}")
        individual_ints.append(int(b.bin, 2))
    jz = ",".join(map(repr, individual_ints))
    individual_z_levels.append(jz)

print(".".join(individual_z_levels))

jzl = "".join(individual_z_levels).replace(",", "")
