#reverse complement we did on day 3 can be done by calling it function ,even so whatever we learned so far can be call function 

def reverse_complement(dna):
    pairs = {"A":"T","T":"A","G":"C","C":"G"}
    complement=""
    for base in dna:
        complement += pairs[base]
    return complement[::-1]

print(reverse_complement("ATGC"))
print(reverse_complement("AACG"))

def transcribe(coding_dna):
    return coding_dna.replace("T","U")

print(transcribe(reverse_complement("AACG")))