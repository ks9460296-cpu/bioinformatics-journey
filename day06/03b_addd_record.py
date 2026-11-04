# Adds a record to the END of sample.fasta ("a" = append mode)
# Run this BEFORE 03_read_fasta.py; running it twice adds the record twice
with open("sample.fasta", "a") as f:
    f.write(">seq3\n")
    f.write("ATG\n")