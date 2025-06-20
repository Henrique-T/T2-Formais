# Regular Expression to AFD Converter and Lexer

This project parses regular expressions, constructs their deterministic finite automata (AFDs), and performs lexical analysis over input text using the generated automaton.

---

## How to Run

Make sure you're inside the `\T1\src` directory and run:

```bash
python main.py
```

Python 3.8+ is recommended.

## Input Files
These files must exist before running the program:

1. ../example_input_RE.txt – contains regular expression definitions, 
    one per line (e.g., ID: (a|b)*abb#)

2. ../example_test_input.txt – the source text to be analyzed by the lexer

Both paths are hardcoded in main.py via global variables:

```
INPUT_RE_FILE = "../example_input_RE.txt"
INPUT_USER_FILE = "../example_test_input.txt"
```

## Output files
The following files are generated automatically:

1. ../afd_output_{i}.txt – AFD representation for the i-th regular expression

2. ../token_list_output.txt – Token list resulting from lexical analysis of the input source

Global output file variable in main.py:
```
OUTPUT_TOKEN_LIST_FILE = "../token_list_output.txt"
```

## Process Overview
### Read and Parse Regular Expressions

    Parses each line of example_input_RE.txt into a RegularExpression object.
    *No outputs for this.*

### Convert to Postfix Notation

    Tokenizes and converts each regular expression to postfix.
    *No outputs for this. If you want to print out the postfix, uncomment line 35 in main.py.*

### Build Syntax Tree

    Constructs a syntax tree using the postfix expression.
    *No outputs for this. If you want to print out the syntax tree, uncomment line 41 in main.py. However, the bigger the input RegEx, the bigger the tree. Be aware.*

### Compute Tree Properties

    Calculates nullable, firstpos, lastpos, and followpos values.
    *No outputs for this. If you want to print out the followpos, uncomment line 46 in main.py. However, the bigger the input RegEx, the bigger the followpos. Be aware.*

### Build AFD

    Converts the syntax tree into a deterministic finite automaton (AFD).
    *AFD is saved as afd_output_{i}.txt.*

### Create Union of AFDs

    Unifies all AFDs into one.
    *No outputs for this. If you want to print out the afd, uncomment line 61 in main.py. However, the bigger the input RegEx, the bigger the afd. Be aware.*

### Run Lexer

    Uses the unified AFD to tokenize the input text from example_test_input.txt.
    *Writes the token list to token_list_output.txt.*

## Example output

```
Starting regular expression to AFD conversion...

Parsing regEx 1: id: [a-zA-Z]([a-zA-Z] | [0-9])*

#1.Tokenize and create postfix format for regular expression

     RegEx to Postfix done.

#2.Build syntax tree

     Build Syntax Tree done.

#3.Computing nullable, firstpos, lastpos, and followpos

     Nullable, firstpos, lastpos, and followpos done.

#4.Build AFD

     AFD built.

     File saved: ../afd_output_0.txt

#5.Union with epsilon transitions

     Union done.

#6.Lexer Analysis

     Token list built.

     File saved: ../token_list_output.txt

```

# Input Examples
## RegEx to be included in example_input_RE.txt
1. id: [a-zA-Z]([a-zA-Z] | [0-9])*
2. num: [1-9]([0-9])* | 0
3. er1: a?(a | b)+
4. er2: b?(a | b)+

## Source text to be include in example_test_input.txt
1. a1
2. 0
3. teste2
4. 21
5. alpha123
6. 3444
7. a43teste
8. aa
9. bbbba
10. ababab
11. bbbbb