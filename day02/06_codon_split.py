dna = "ATGCGTGCAT"

codons = []                                  # Lesson 1: empty list
for i in range(0, len(dna) - 2, 3):          # Lessons 3-4: loop over start positions
    codons.append(dna[i:i + 3])              # Lessons 2 and 5: cut 3 letters, add to list
print(codons)                                # outside the loop: runs once
print("Number of codons:", len(codons))