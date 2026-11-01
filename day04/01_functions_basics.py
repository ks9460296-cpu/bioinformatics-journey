#function is a named block of code you write once and reuse it . some function we have use already like len(dna) and print(...) 

#def function_name(input)
#     ...do something...
# return result 

#def means “I’m defining a function”.
# The name in brackets, called a parameter, is the input. It’s a placeholder variable.
# return sends the answer back to whoever called the function.
# The body is indented 4 spaces, like a loop.

def gc_count(dna):
    return dna.count("G") + dna.count("C")
# what we did here instead of writting whole code for gc_count everytime we create a function for it and now we can call it and use it directly , we write the code once and turn it into function now we use it as many times we want 
print(gc_count("ATGCGT"))
print(gc_count("GGGG"))

result = gc_count("ATGC")
print(result)


def at_count(dna):
    return dna.count("A") + dna.count("T") 

print(at_count("ATTTAGGTACTATACTA"))