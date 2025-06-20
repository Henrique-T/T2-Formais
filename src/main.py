import regular_expression as re
import syntax_tree as st
import afn
import automaton_operations as ao
from lexer_simulation import run_lexer
from functools import reduce

INPUT_RE_FILE = "../example_input_RE.txt"
INPUT_USER_FILE = "../example_test_input.txt"
OUTPUT_TOKEN_LIST_FILE = "../token_list_output.txt"

def main():
    log_step("Starting regular expression to AFD conversion...")
    regular_expressions = []
    try:
        with open(INPUT_RE_FILE, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if line:
                    log_step(f"Parsing regEx {line_number}: {line}")
                regular_expressions.append(re.RegularExpression.from_definition_line(line))
    except FileNotFoundError:
        print(f"Error: The file '{INPUT_RE_FILE}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    names = []
    afns = []
    for i, regex in enumerate(regular_expressions):
        names.append(regex.name)

        log_step("#1.Tokenize and create postfix format for regular expression")
        postfix = regex.to_postfix(regex.pattern)
        log_success("     RegEx to Postfix done.")
        #log_success(postfix) # --> uncomment this to log on console.

        log_step("#2.Build syntax tree")
        tree = st.SyntaxTree(postfix)
        root = tree.build_syntax_tree()
        log_success("     Build Syntax Tree done.")
        #tree.log_syntax_tree(root) # --> uncomment this to log on console.

        log_step("#3.Computing nullable, firstpos, lastpos, and followpos")
        followpos = tree.compute_nullable_first_last_follow(root)
        log_success("     Nullable, firstpos, lastpos, and followpos done.")
        #log_success(followpos) # --> uncomment this to log on console.

        log_step("#4.Build AFD")
        afd = st.build_afd(root, followpos, tree.leaf_positions)
        afd.export_to_txt(f"../afd_output_{i}.txt")
        log_success("     AFD built.")
        log_done(f"../afd_output_{i}.txt")

    for i, name in enumerate(names):
        afns.append(afn.AFN.load_afd_from_file(f"../afd_output_{i}.txt", token_type=name))

    log_step("#5.Union with epsilon transitions")
    union_afn = reduce(lambda a1, a2: ao.AutomatonOperations.union(a1, a2), afns)
    afd, token_map = union_afn.to_afd()
    log_success("     Union done.")
    #log_success(afd) # --> uncomment this to log on console.

    log_step("#6.Lexer Analysis")
    run_lexer(afd, token_map, INPUT_USER_FILE, OUTPUT_TOKEN_LIST_FILE)
    log_success("     Token list built.")
    log_done(f"{OUTPUT_TOKEN_LIST_FILE}")


def log_step(msg):
    print(f"{msg}")
    print("")

def log_success(msg):
    print(f"{msg}")
    print("")

def log_export(file):
    print(f"Exporting to {file}...")
    print("")

def log_done(file):
    print(f"     File saved: {file}")
    print("")

if __name__ == "__main__":
    main()