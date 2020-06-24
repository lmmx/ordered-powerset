from ord_pset.bit_strings import bitstream_ins
from ord_pset.tests.data.bit_strings_target_values import (
    binstream_lossless_targets,
    binstream_lencode_targets,
    binstream_fixed_len_targets,
)


def test_bitstream_ins_lossless():
    for n in range(65):
        bs = bitstream_ins(n=n, fixed_length=False, lencode=False)
        binval = bs.bin
        assert binval == binstream_lossless_targets[n], ValueError(
            f"Result {n} did not match target string: {binval} ≠ {binstream_lossless_targets[n]}"
        )
    return


def test_bitstream_ins_lencode():
    for n in range(69):
        bs = bitstream_ins(n=n, fixed_length=False, lencode=True)
        binval = bs.bin
        assert binval == binstream_lencode_targets[n], ValueError(
            f"Result {n} did not match target string: {binval} ≠ {binstream_lencode_targets[n]}"
        )
    return


def test_bitstream_ins_fixed_len():
    for n in range(65):
        bs = bitstream_ins(n=n, fixed_length=True, lencode=False)
        binval = bs.bin
        assert binval == binstream_fixed_len_targets[n], ValueError(
            f"Result {n} did not match target string: {binval} ≠ {binstream_fixed_len_targets[n]}"
        )
    return
