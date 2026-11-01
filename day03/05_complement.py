#dictionary + loop 


dna = "ATGC"
pairs = {"A":"T","T":"A","G":"C","C":"G"}

complement = ""  #create an empty string 

for base in dna:
    complement+= pairs[base] #+= will add complement+pairs[base]
    #pairs[base] will assign partner letter like A to T 
print(complement)



dna = "GATTACA"
pairs = {"A":"T","T":"A","G":"C","C":"G"}

complement= ''

for base in dna :
    complement += pairs[base]
print(complement)