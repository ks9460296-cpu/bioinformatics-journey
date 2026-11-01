#DNA's second strand is the complemenatry .A pairs with T and G pairs with C .so the complement of ATGC should be TACG 

#the obvious idea : swap A for T and then T for A .

dna = "ATGC"

step1 = dna.replace("A","T")
print(step1)

step2 = step1.replace("T","A")
print(step2)


# Both are correct: TTGC, then AAGC. That’s the problem.

# The right complement of ATGC is TACG, and yours ended as AAGC. The first two letters are both A, because the original A and the original T collided:

# Step 1 turned the A into T, so now there are two T’s and no way to tell which was original.
# Step 2 turned every T into A, including the one that was already a T at the start.

# replace works on the whole string at once, so the second swap undoes part of the first. We need a method that handles each letter exactly once.
