#range gives the start position and slicing cuts a piece from each one ,together they chop a sequence into equal pieces.

dna = "ATGCGTGCA"
print(list(range(0,len(dna),3))) #start from 0 to all the way to the end of dna and step by 3 each time ,so it will give 0,3,6

for i in range(0,len(dna),3):
    print(dna[i:i+3])# i = start position ,i+3 = end position ,so it will cut out the three letters starting at position i and print them 

# if dna has 10 letters, what does list(range(0, len(dna) - 2, 3)) give? Work it out in steps:

# What is len(dna) - 2?
# Which numbers start at 0, jump by 3, and stay below that?

# Step 1: do the maths.

# len(dna) is 10 (the sequence has 10 letters).
# 10 - 2 = 8.

# So the line range(0, len(dna) - 2, 3) becomes range(0, 8, 3).

# Step 2: read it as start, stop, step.

# Start at 0.
# Stop before 8.
# Jump by 3 each time.

# Step 3: list the numbers.

# 0 is below 8, so it’s included.
# 0 + 3 = 3 is below 8, so it’s included.
# 3 + 3 = 6 is below 8, so it’s included.
# 6 + 3 = 9 is not below 8, so it stops.

# Result: [0, 3, 6]. Position 9 is gone, which means the leftover T is never cut out as a short piece.