## Day 6 | 2026-11-02 to 2026-11-03

**Concepts Mastered**
- Files: `open()` with modes `"w"` (wipes), `"a"` (appends), `"r"` (reads); `with` closes the file automatically
- A file name is looked up in the folder the script is RUN from
- Every line read ends with a hidden `\n`; `.strip()` removes it
- FASTA: `>` header line, then sequence lines (can wrap over several lines)
- `.startswith()`, `continue`, `None`, `.items()`
- Parsing FASTA into a dictionary {name: sequence}
- Debugging: `FileNotFoundError`, `NameError` (`none` vs `None`), `KeyError: None` from a bad data file

**Tools & Libraries Used**
- Python 3.14.4 built-ins, VS Code on WSL: Ubuntu, `cat -A` to show hidden characters

**Code / Practical Implementation**
- `01_write_read.py` to `04_fasta_to_dict.py`; `sample.fasta` with 3 records (16, 8 and 3 bases)

**Key Takeaways & Next Milestone**
- Check data files with `cat -A` before blaming the code
- Next (Day 7): wrap the parser in a function, use `input()`, validate DNA