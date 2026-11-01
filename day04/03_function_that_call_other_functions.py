#a function can call other functions too ,small tools combine into bigger one 

def gc_count(dna):
    return dna.count("G") + dna.count("C")

def gc_percent(dna):
    return gc_count(dna)/len(dna)*100

def classify_gc(dna):
    percent = gc_percent(dna)
    if percent>60:
        return "GC-rich"
    elif percent >= 40:
        return "moderate GC"
    else:
        return "GC-poor"

print(gc_percent("ATGTCGTCGATAGGA"))
print(classify_gc("ATTGGACCAAGATAGACAGATACAGTA"))
print(classify_gc("ATTAGGAGACACAAGTAAACC"))
print(classify_gc("ATTAGCCCAACCCGGTAGTACA"))


# What to notice:

# gc_percent doesn’t repeat any counting. It calls gc_count, which is the Day 1 idea of “write it once, reuse it.”
# classify_gc calls gc_percent, so there’s a chain: classify calls percent, which calls count.
# return can sit inside an if/elif/else. Only the first matching branch runs, and the function ends right there.
# Order matters: a function must be defined above the line that calls it, the same as with variables.


