# RECAP: list vs tuple vs set vs dictionary

# LIST [ ]
#   keeps order, can change, allows duplicates, pick by position x[0]
#   use for: codons in reading order, a result that keeps growing

# TUPLE ( )
#   keeps order, can NOT change, allows duplicates, pick by position x[0]
#   use for: fixed pairs like (start, end) or (gene, chromosome)

# SET { }
#   no order, can change, NO duplicates, no picking (only "in")
#   use for: unique bases or unique codons

# DICTIONARY { key: value }
#   keeps order, can change, keys can't repeat, pick by key x["A"]
#   use for: tallies (counts) and lookup tables (pairs)

codons = ["ATG", "CGT", "ATG"]
gene = ("TP53", 17)
unique = {"ATG", "CGT"}
counts = {"A": 9, "T": 8}

print(type(codons))
print(type(gene))
print(type(unique))
print(type(counts))

# Your exercise is the same as before. For each job, choose the best structure and write a one-line reason as a comment:

# Store the codons of a gene in reading order.  answer list
# Count how many times each base appears.   answer dictionary 
# Store a gene’s start and end positions, which won’t change.  answer tuple 
# Find which different codons a gene uses.   answer set
