# Day 6, Lesson 2: reading a file line by line
#
# NOTES
# - "w" = write: creates the file, or WIPES it if it already exists
# - "a" = append: adds to the end, keeps old content
# - "r" = read: reads only; error if the file doesn't exist
# - A file name is looked up in the folder I RAN the script from
# - Every line read from a file ends with \n (a hidden newline character)
# - .strip() removes whitespace and newlines from BOTH ends of a string
# - len() counts every character, including hidden ones like \n

# 1. Make the file (wipes sample.txt if it exists)
with open("sample.txt", "w") as f:
    f.write("ATGCGT\n")      # \n = start a new line
    f.write("GGCCAA\n")

# 2. Read it one line at a time
with open("sample.txt", "r") as f:
    for line in f:                      # line is the next line each pass, e.g. "ATGCGT\n"
        seq = line.strip()              # remove the \n, keep the letters
        print(seq, len(seq))            # without strip, len would be 7, not 6