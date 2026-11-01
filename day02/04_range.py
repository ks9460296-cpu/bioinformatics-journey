#range produces a sequence of numbers , so a for loop can count instead of walking through a list or string

#three forms :
#rnage(5) gives 0,1,2,3,4 (start at 0 and stop before 5)
#range(2,5) gives 2,3,4 (start at 2 and stop before 5)
#range(0,10,2) gives 0,2,4,6,8 (start at 0 and stop before 10 and step by 2)

#the stop number is never included ,which is the same "end excluded" rule as slicing a string or list


#range : produce numbers to loop over 
print(list(range(5))) #print the numbers 0,1,2,3,4
#list just turns the range into a list so we can see it printed out
print(list(range(2,5))) #print the numbers 2,3,4
print(list(range(0,10,2))) #print the numbers 0,2,4,6,8

print("----")

for i in range(5): #loop through the numbers 0,1,2,3,4
    print(i) #print each number in the loop


# print("range(0, 12, 3)")   # text: prints exactly range(0, 12, 3)
# print(range(0, 12, 3))     # a command: Python runs range, gets a range object, prints it

# what’s the difference between print(len("dna")) and print(len(dna)) if dna = "ATGCGT"? Answer in your own words, then run both.

dna = "ATGCGT"
print(len("dna"))   # 3
print(len(dna))     # 6
print("dna")        # dna  (the word)
print(dna)          # ATGCGT (the variable's value)

# what does print(list(range(0, 12, 3))) show, and how many numbers? Tell me your prediction, then run it.Start at 0, so the first number is 0.
# Add 3 to get 3, then add 3 again for 6, and again for 9.
# The next would be 12, but the stop number is never included, so it ends.
# [0, 3, 6, 9]