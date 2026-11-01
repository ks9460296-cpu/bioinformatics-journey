# Daily Log

## Day 1 | 2026-10-21
**Concepts Mastered**
- Why bioinformatics runs on Linux; WSL2 as Linux inside Windows
- A DNA sequence is a Python string; variables store a value for reuse
- 0-based indexing and slicing (`dna[:3]`, `dna[-3:]`)
- GC content = (G + C) / length x 100

**Tools & Libraries Used**
- WSL2 (Ubuntu), Python 3.14.4, VS Code (WSL, Python, Pylance, Ruff)
- Bash: `cd`, `mkdir -p`, `code .`

**Code / Practical Implementation**
- `hello_dna.py`: length, base counts, GC count and GC% of a 34-base sequence

**Key Takeaways & Next Milestone**
- Define a variable before using it; check counts against length
- Next: lists, dictionaries, loops

## Day 2 | 2026-10-21
**Concepts Mastered**
- Dictionary as a tally (`counts[base] += 1`); lists and `.append()`
- `for` loops, `range(start, stop, step)`, slicing with a variable
- Codons: DNA is read 3 bases at a time; TAA is a stop codon
- Indentation decides what repeats

**Tools & Libraries Used**
- Python 3.14.4, VS Code on WSL; Bash: `mv`, `ls`, `touch`, `mkdir`

**Code / Practical Implementation**
- `nucleotide_dict.py`: base counts and codon splitting (11 codons + 1 leftover base from 34)

**Key Takeaways & Next Milestone**
- `len(dna) - 2` stops the loop from starting an incomplete codon
- Next: conditions, string methods, complement

## Day 3 | 2026-10-21 to 2026-10-22
**Concepts Mastered**
- `if` / `elif` / `else`, comparisons, `in`
- `.upper()`, `.lower()`, `.replace()`; DNA to RNA
- Why chained `.replace()` fails for complements
- Complement via dictionary + loop; slicing with a step; `[::-1]` reverses
- Reverse complement = complement, read backwards

**Tools & Libraries Used**
- Python 3.14.4, VS Code on WSL

**Code / Practical Implementation**
- GC-rich / moderate / GC-poor classifier; `05_complement.py`; reverse complement (GATTACA -> TGTAATC)

**Key Takeaways & Next Milestone**
- `[ ]` looks things up, `( )` calls functions
- Next: functions

## Day 4 | 2026-10-22
**Concepts Mastered**
- Functions: `def`, parameters, `return`, local scope
- Functions calling functions; multiple parameters; default values
- Returning two values (a tuple)
- DNA to coding strand to mRNA

**Tools & Libraries Used**
- Python 3.14.4 (built-ins: `round`, `len`), VS Code on WSL

**Code / Practical Implementation**
- `gc_count`, `at_count`, `reverse_complement`, `gc_percent`, `classify_gc`, `percent_of`, `gc_summary`

**Key Takeaways & Next Milestone**
- Write once, reuse many times; define a function above where it's called
- Next: tuples, sets, then files and FASTA parsing