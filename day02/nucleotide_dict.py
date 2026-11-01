# count = {} makes an empty  dictionary 
# for base in dna : visits each letter ,one at a time 
#if base in counts : ask 'have i seen this letter already?' if yes add 1, if no,start it at 1 
#range(0, len(dna) -2 , 3) jumps through posiyion 0,3,6,9 and so on 
#dna[i:i+3]cuts out the three letters starting at position i 
#codons.append(......)adds each slice to the list 


dna = "ATGCGTGCATGCAATGCAAAGTCTTAAGGCCTCG"

# counts = {} #empty dictionary to hold counts of each base
# for base in dna : # go through each letter in the dna string
#     if base in counts : # have i seen this letter already?
#         counts[base] += 1 # x = 5 ,x += 1 is the same as x = x + 1, so if i have seen this letter before,
#          #yes add 1 to the value of that letter in the dictionary
#     else : # no create it with value 1
#         counts[base] = 1

# print(counts)

#counts = {} create an empty dictionary , for loop visit each base in dna ,if base in dna +1 add or else create it with value 1 , print the dictionary with counts of each base in dna


codons = [] #empty list to hold codons
for i in range(0,len(dna) -2,3): #go through the dna string in steps of 3, starting at position 0, then 3, then 6, then 9 and so on
    codons.append(dna[i:i+3]) #cut out the three letters starting at position i and add it to the list
print(codons) #print the list of codons
print("number of codons:",len(codons)) #print the number of codons in the list