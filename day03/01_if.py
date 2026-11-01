#if and else let code make a decision based on a condition .python checks the condition and if it is true it executes the code in the if block otherwise it executes the code in the else block. 


#comparison operators are used to compare values and return a boolean value (True or False). The most common comparison operators are:
# == : equal to
# != : not equal to
# > : greater than
# < : less than
# >= : greater than or equal to
# <= : less than or equal to

gc_percent = 62.5 

print(gc_percent > 50)
print(gc_percent < 50)

if gc_percent > 50:
    print("GC-rich sequence")
else:
    print("AT-rich sequence")