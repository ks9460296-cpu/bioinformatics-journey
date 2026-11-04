# Demo : "a"(append) vs "w"(write) mode
# "w" mode wipes the file if it exists, "a" mode adds to the end of the file, keeping the old content

# 1. start fresh : one line 
with open("append_test.txt", "w") as f:
    f.write("ATGCGT\n")

# 2. append a line
with open ("append_test.txt", "a") as f:   #keep in mind that append function as stacking ,so as many times u run the file it keep adding the new line to the end of the file, so if you run the file 3 times, it will add 3 lines of "GGCCAA" to the end of the file
    f.write("GGCCAA\n")

# 3. read the file
with open ("append_test.txt","r") as f:
    for line in f:
        print(line.strip())


# 4. wipe the file and write a new line
with open("append_test.txt", "w") as f:  #as we use "w" mode, the file is wiped and we can write a new line ,old data deleted
    f.write("TTGCAA\n")