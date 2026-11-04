# Day 6, Lesson 3: reading a FASTA file
# - a line starting with ">" is a header (the name)
# - other lines are sequence; one record can span many lines
# - .startswith(">") asks: does this line begin with ">"?
# - line[1:] slices from position 1, which drops the ">"

with open("sample.fasta","r") as f:
    for line in f:
        line = line.strip()         # remove the \n, keep the letters
        if line.startswith(">"):    # if the line starts with ">", it's a header
            print("HEADER:",line[1:])  # print the header, dropping the ">"
        else:                       # otherwise, it's a sequence line
            print("SEQ:",line, len(line))    # print the sequence line and its length


# What to notice:

# seq1 has two sequence lines (10 + 6 letters). The program doesn’t yet know they belong together, and Lesson 4 fixes that.
# line = line.strip() reuses the same name for the cleaned copy. That’s allowed.