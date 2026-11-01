#a function can return severalvalues at once ,separatedby commas.python packs them into a tuple, which is a kind of list that can't be changed. You can unpack the tuple into several variables, or just use the tuple as a single value.

def gc_summary(dna):
    gc= dna.count("G")+dna.count("C")
    percent= gc/len(dna)*100
    return gc, percent

print(gc_summary("ATGCGT"))

gc,percent = gc_summary("ATGCGT")
print(gc)
print(percent)

#What to notice:

# return gc, percent sends back both values together.
# Printing the call directly shows the bundle in round brackets, which is the tuple.
# gc, percent = gc_summary(...) unpacks it: the first value goes into gc, the second into percent. The order matches the return.