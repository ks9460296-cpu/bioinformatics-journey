# for loop : repeat a step for every item

dna = "ATGC"
for base in dna : #go through each letter in the dna string
    print(base) #print each letter in the dna string

print("----")

codons = ["ATG","CGT","GCA"]
for codon in codons : #go through each item in the codons list
    print(codon) #print each item in the codons list

print("----")
# the loop with append : repeat a step for every item and add it to a list
letters = [] #empty list to hold bases
for base in dna: #loop visit each letter in the dna string
    letters.append(base) #on each pass through the loop, add the letter to the list from base in dna
    print(letters) #print the list of bases in letters
     #add identation to see it happen or remove it to see the final list at the end of the loop

#predict then run : if dna = "GATTACA" has 7 letters, how many times will the loop run and what will be printed each time?