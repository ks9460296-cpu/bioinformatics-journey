codons = ["ATG", "CGT", "ATG"]

# lists -> tuple ,and back 
codons_tuple = tuple(codons)
print(codons_tuple)
back_to_list = list(codons_tuple)
print(back_to_list)

# lists _> set (duplicate removal) 
unique = set(codons)
print(unique)
print(len(unique))  # Output will be 2, since there are 2 unique codons: ATG, CGT

#tuple _> set 
unique_from_tuple = set(codons_tuple)
print(unique_from_tuple)


# set _> sorted list ( so it has an order )
print(sorted(unique))  # Output will be ['ATG', 'CGT'] - sorted list of unique codons


# strings _> list or tuple of letters
print(list("ATGGC"))  # Output will be ['A', 'T', 'G', 'G', 'C']
print(tuple("ATGGC"))  # Output will be ('A', 'T', 'G', 'G', 'C')
print(set("ATGGC"))  # Output will be {'A', 'T', 'G', 'C'} - unique letters
print(sorted("ATGGC"))  # Output will be ['A', 'C', 'G', 'G', 'T'] - sorted list of letters
print(sorted(set("ATGGC")))  # Output will be ['A', 'C', 'G', 'T'] - unique letters sorted