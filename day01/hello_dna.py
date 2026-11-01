# Day 1: variables, strings, basic operations on DNA
# dna = "ATGCGTACGTTAGC"

# print("Sequence:", dna)
# print("Length:", len(dna))
# print("Count of A:", dna.count("A"))
# print("Count of G:", dna.count("G"))

# gc = (dna.count("G") + dna.count("C")) / len(dna) * 100
# print(f"GC content: {gc:.2f}%")

# print("Lowercase:", dna.lower())
# print("First codon:", dna[:3])


dna = "ATGCGTGCATGCAATGCAAAGTCTTAAGGCCTCG"

print("sequence:", dna)
print("length:",len(dna))
print("count of A:",dna.count("A"))
print("count of G:",dna.count("G"))
print("count of C:",dna.count("C"))
print("count of T:",dna.count("T"))

GC_count = dna.count("G") + dna.count("C")

print("GC count:", GC_count)
print("GC percentage:", GC_count / len(dna) * 100)

print("last codon:",dna[-3:])