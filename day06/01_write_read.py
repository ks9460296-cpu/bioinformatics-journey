# write a small text file

with open("sample.txt","w") as f:  #open("sample.txt","w") opens a file to write, if it exists it will overwrite the file, if it doesn't exist it will create a new file
    f.write("ATGCGT\n")  # write a string to the file, \n is a newline character
    f.write("GCTAGC\n")  # write another string to the file


# read the small text file
with open("sample.txt","r") as f:  #open("sample.txt","r") opens a file to read
    text = f.read()  # read the entire file into a string
print(text)
print(len(text))  # print the length of the string  # how 14 = 7 + 7, because there are 2 lines of 6 characters each, plus 2 newline characters (\n) , 6 letters + 1 newline + 6 letters + 1 newline = 14

print(repr(text))  # print the string with escape characters visible, so we can see the newline characters