# Regular Expression to AFD Converter, Lexer, and SLR Parser

This project performs **lexical and syntactic analysis** for a source input file using:

- Regular Expressions → Syntax Tree → AFD
- Lexer to tokenize source code
- SLR Parser to check syntactic validity via a context-free grammar (CFG)

---

## How to Run

Make sure you're inside the `\T2-Formais\src` directory and run:

```bash
python main.py
```

Python 3.8+ is recommended.

# Mode selection
The behavior of the program is controlled by the variable ONLY_PARSER_MODE located in main.py:
```
ONLY_PARSER_MODE = False  # Full lexer + parser pipeline
ONLY_PARSER_MODE = True   # Only run the SLR parser from token_list_output.txt

```
## Full Pipeline Mode (False)
Runs from scratch: converts regex → builds AFDs → lexes source text → builds parsing table → parses.

## Parser-Only Mode (True)
Skips lexical analysis and uses the pre-existing file:
```
./output/token_list_output.txt
```

# Input Files
These files must exist before running the program:

1. ./input/example_input_RE.txt – contains regular expression definitions, 
    one per line (e.g., ID: (a|b)*abb#)

2. ./input/example_test_input.txt – the source text to be analyzed by the lexer

3. ./input/example_input_grammar.txt - The context-free grammar (CFG) in the format,
    one production per line (e.g., S ::= A B)

All paths are hardcoded in main.py via global variables:

```
INPUT_RE_FILE = "../example_input_RE.txt"
INPUT_USER_FILE = "../example_test_input.txt"
INPUT_GRAMMAR_FILE = "./input/example_input_grammar.txt"
```

# Output files
The following files are generated automatically:

1. ./output/afd_output_{i}.txt – AFD representation for the i-th regular expression

2. ./output/token_list_output.txt – Token list resulting from lexical analysis of the input source

3. ./output/first_output.txt – FIRST sets for all non-terminals.

4. ./output/follow_output.txt – FOLLOW sets for all non-terminals.

5. ./output/lr0_states.txt – LR(0) items (states) generated by the canonical collection algorithm.

6. ./output/lr0_transitions.txt – State transitions for the LR(0) items.

7. ./output/slr_action_table.txt – ACTION table for the SLR parser.

8. ./output/slr_goto_table.txt – GOTO table for the SLR parser.


Global output file variable in main.py:
```
OUTPUT_TOKEN_LIST_FILE = "../token_list_output.txt"
```

# Process Overview

## Phase 1: Lexical Analysis (skipped if ONLY_PARSER_MODE = True)

1. Parse Regular Expressions
    Converts each line of example_input_RE.txt into a syntax tree.

2. Build AFDs and Merge Them
    Each regex → AFD → merged into a single AFD with ε-transitions.

3. Run Lexer
    Tokenizes example_test_input.txt into token_list_output.txt.

## Phase 2: Syntactic Analysis

4. Load Grammar
    CFG is read from example_input_grammar.txt.

5. Compute FIRST and FOLLOW Sets
    Saves to first_output.txt and follow_output.txt.

6. Build LR(0) Item Sets
    Closure and goto operations → lr0_states.txt, lr0_transitions.txt.

7. Build SLR Table
    ACTION and GOTO tables built → slr_action_table.txt, slr_goto_table.txt.

8. SLR Parsing
    Parses the token list and prints:

    - Sentence Accepted!

    - Sentence Rejected!


# Example Inputs

Regular Expressions (example_input_RE.txt)
```
for: for
if: if
else: else
id: [a-zA-Z][a-zA-Z0-9]*
```

Source Text (example_test_input.txt)
```
for 
x 
if 
y 
else 
z
```

Grammar (example_input_grammar.txt)
```
S ::= for E
S ::= if E else E
S ::= id
E ::= id
```

## Example Output

```
C:\Users\samsung\Desktop\Formais\T2-Formais\src>python main.py

 Starting regular expression to AFD conversion...


      Parsing regEx 1: for: for


      Parsing regEx 2: if: if


      Parsing regEx 3: else: else


      Parsing regEx 4: id: [a-zA-Z][a-zA-Z0-9]*


 #1. Tokenize and create postfix format for regular expression


 #2. Build syntax tree


 #3. Computing nullable, firstpos, lastpos, and followpos


 #4. Build AFD

 File saved: ./output/afd_output_0.txt


 #1. Tokenize and create postfix format for regular expression


 #2. Build syntax tree


 #3. Computing nullable, firstpos, lastpos, and followpos


 #4. Build AFD

 File saved: ./output/afd_output_1.txt


 #1. Tokenize and create postfix format for regular expression


 #2. Build syntax tree


 #3. Computing nullable, firstpos, lastpos, and followpos


 #4. Build AFD

 File saved: ./output/afd_output_2.txt


 #1. Tokenize and create postfix format for regular expression


 #2. Build syntax tree


 #3. Computing nullable, firstpos, lastpos, and followpos


 #4. Build AFD

 File saved: ./output/afd_output_3.txt


 #5. Union with epsilon transitions


 #6. Lexer Analysis

 File saved: ./output/token_list_output.txt


 #7. Interpret grammar


 #8. Calculate FIRST and FOLLOW sets

 File saved: ./output/first_output.txt

 File saved: ./output/follow_output.txt


 #9. Build set of LR(0) items (Closure & Goto)

 File saved: ./output/lr0_states.txt

 File saved: ./output/lr0_transitions.txt


 #10. Build SLR parsing table

 File saved: ./output/slr_action_table.txt

 File saved: ./output/slr_goto_table.txt


 #11. Run SLR parsing

Sentence accepted!

------ Symbol Table ------
1: for (PR)
2: x (ID)

Sentence Accepted!
```