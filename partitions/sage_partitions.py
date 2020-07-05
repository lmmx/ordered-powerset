# Sage
def comb_partitions(n):
    for r in range(n):
        r_partitions = []
        for l in range(0,r+1):
            l_partitions = Partitions(r, length=l).list()
            r_partitions.extend(l_partitions)
        print(f"{r}", r_partitions)

def q_multinom_partitions(n):
    for r in range(n):
        partition_path_counts = []
        for l in range(0,r+1):
            l_partitions = Partitions(r, length=l).list()
            q_multinoms = [q_multinomial(p) for p in l_partitions]
            q_multinoms = [q if type(q) is sage.rings.integer.Integer else sum(q.coefficients()) for q in q_multinoms]
            partition_path_counts.extend(q_multinoms)
        print(f"{r}", partition_path_counts)
