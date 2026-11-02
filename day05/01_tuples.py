# 1.a tuple is an ordered collection, writtenwith () .it can't be changed 

gene = ("TP53",17,7668402)
print(gene)
print(gene[0])
print(len(gene))

# 2. unpacking : put each item into its own variable ,in order name, chromosome,position = gene 
name, chromosome, position = gene
print(name)
print(chromosome)
print(position)

# 3. lists can change,tuples cannot 
# gene[0] = "BRCA1"  # This would cause an error because tuples are immutable
codons = ["ATG", "TGG", "TAA"]
codons[0] = "ATC"  # This is fine because lists are mutable
print(codons)

# 4. tuples can be used as keys in dictionaries, lists cannot
gene_dict = {("TP53", 17): "Tumor protein p53", ("BRCA1", 17): "Breast cancer type 1 susceptibility protein"}
print(gene_dict[("TP53", 17)])  # Accessing value using a tuple as a key

# 5.workaround for changing a tuple: convert to list, change, convert back to tuple ,this builds a new tuple with the changes,leaving the original tuple unchanged

temp = list(gene)  # Convert tuple to list
temp[0] = "BRCA1"  # Change the first element
gene = tuple(temp)  # Convert back to tuple
print(gene)  # Now gene is ("BRCA1", 17, 7668402)

# temp is just a variable name i chose. it's short for "temporary",meaming that it is only used for a short time to hold the list version of the tuple while we make changes.