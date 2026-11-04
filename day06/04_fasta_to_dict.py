# Concept: right now seq1 is split across two lines, and the program doesn’t know they belong together. We fix that by building a dictionary, {name: sequence}, and joining each record’s lines as we go. It’s the first parser you’ll write, and the same idea sits behind Biopython’s FASTA reader




# Day 6, Lesson 4: FASTA -> dictionary {name: sequence}
# - on a ">" line: start a new record with an empty sequence
# - on any other line: add it to the current record's sequence
# - .items() gives (key, value) pairs when looping over a dictionary






records = {}
name = None

with open("sample.fasta","r") as f:
    for line in f:
        line = line.strip()
        if line.startswith(">"):
            name = line[1:]  # remove the ">" and store the name
            records[name] = ""  # initialize an empty sequence for this name
        else:
            records[name] += line  # append the sequence line to the current record

for name, seq in records.items():
    print(name, len(seq))