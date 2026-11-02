# a set is a collection of unique items.add the same thing twice and it's kept once .it written with curly braces {} or with the set() function .sets are unordered and unindexed so u can't use x[0] on it .they are mutable but can't contain mutable items like lists or dictionaries

# 1. A set keeps only unique items
bases = {"A","T","G","C","A","T"}  # "A" and "T" are duplicates
print(bases)# Output will be {'A', 'T', 'G', 'C'} - duplicates are removed
# print(bases[0])  # This will cause an error because sets are unordered and unindexed ,error message will be: TypeError: 'set' object is not subscriptable


# 2. unique lettes in a sequence : set() can be used to find unique letters in a string
dna = "ATGCGTAAGC"
unique_bases = set(dna) # Convert string to set to get unique characters
print(len(unique_bases))  # Output will be 4, since there are 4 unique bases: A, T, G, C
print(sorted(unique_bases))  # Output will be ['A', 'C', 'G', 'T'] - sorted list of unique bases,sorted means put in order from smallest to largest,for letters that means alphabetical order

# 3. addd, and checking membershp with in : use add() to add an item to a set, and use in to check if an item is in the set
stops = {"TAA","TAG","TGA"}
stops.add("TAA")  # Adding a duplicate, will not change the set
print(stops)  # Output will be {'TAA', 'TAG', 'TGA'} - still only unique items
print("TAA" in stops)  # Output will be True, since "TAA" is in the set
print("ATG" in stops)  # Output will be False, since "ATG" is not in the set

# 4. unique codons from a list : use set() to get unique items from a list
codons = ["ATG","CGT","ATG","GCA","CGT"]  # List with duplicates
print(len(codons))  # Output will be 5, since there are 5 items in the list
print(len(set(codons)))  # Output will be 3, since there are 3 unique codons: ATG, CGT, GCA


# Predict the number of unique codons in this list, then check it with len(set(...)):
# codons = ["ATG", "CGT", "GCA", "TGC", "AAT", "GCA", "AAG", "TCT", "TAA", "GGC", "CTC"]
