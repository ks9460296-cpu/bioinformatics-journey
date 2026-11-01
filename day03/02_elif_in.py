#elif means else + if ,it adds more than two outcomes .python checks the conditions from top to bottom and runs only the first one that's true 

#in asks whether something is inside a string or list ,and gives true or false


gc_percent = 45
if gc_percent > 60:
    print("GC-rich sequence")
elif gc_percent>=40:
    print("Moderate GC content")
else:
    print("AT-rich sequence")

dna = "ATGCGTAA"
print("ATG" in dna)
print("TAA" in dna)
print("GGG" in dna)

if "ATG" in dna:
    print("Start codon found")