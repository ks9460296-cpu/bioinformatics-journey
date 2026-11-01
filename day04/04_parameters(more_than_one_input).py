#a function can take several parameters ,separated by commas.A parameter can also have a default value,which is used when u don't supply that input 

def count_base(dna , base):
    return dna.count(base)

def percent_of(dna,base,decimals=1):
    return round(count_base(dna,base)/len(dna)*100,decimals)

print(count_base("ATGCGT","G"))
print(percent_of("ATGCGT","G"))
print(percent_of("ATGCGT","G", decimals=3))

# What to notice:

# When you call count_base("ATGCGT", "G"), Python matches the inputs by position: the first goes to dna, the second to base. Swapping them gives a different (wrong) answer.
# decimals=1 is a default. In the second call you don’t give a third input, so it uses 1. In the third call, you pass 3, which replaces the default.
# round(number, digits) is a built-in function that rounds to that many decimal places.
# Parameters with defaults must come after the ones without.