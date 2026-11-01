#[start:stop:step]

#[0:6:2] start at zero ,stop at 5 ,will step 2 for example ATGCATGC iw will give result AGA 
#[::2]start not defined which means zero will be consider ,stop is also not defined here so we will consider end of string to stop , step is 2 ,for example ATGCATGC it will give result AGAG

#[3:0:1] give empty string  starting point cannot be ahead of stop point 

dna = "ATGCATGC"

print(dna[0:8:2])
print(dna[0:8:1])
print(dna[:8:2])
print(dna[::2])

#line 10,12 and 13 are same just different representation

print(dna[3:0:1])#empty string will be printed logically wrong 

print(dna[1::2]) #why why 
# stop point means go to the end 

print(dna[3:0:-1]) #why why 
#Example: dna[3:0:-1]

# Start at position 3. Pick up C.
# Step left by 1 to position 2. Pick up G.
# Step left to position 1. Pick up T.
# The next stop would be position 0, which is the stop value, and the stop is never picked up. So you halt.

dna = "GATTACA"
pairs = {"A": "T", "T": "A", "G": "C", "C": "G"}

complement = ""
for base in dna:
    complement += pairs[base]

reverse_complement = complement[::-1]
print(complement)
print(reverse_complement)