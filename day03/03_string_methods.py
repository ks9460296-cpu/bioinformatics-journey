#methods are built in tools attached to a string with a dot ,like dna.count("G") from day 1 .Three new ones are .upper() , .lower() , and .replace("old","new") . They don't change the original string ,they return a new one

dna = 'atgcgtaa'
print(dna.upper()) #new string is all uppercase


print(dna) #original string is unchanged

dna= dna.upper() #original string is changed to uppercase
print(dna)


rna= dna.replace("T","U") #new string is RNA with U instead of T
print(rna)

dna= 'ATGCGTAA'
print(dna.replace("A","T"))