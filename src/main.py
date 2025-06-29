from lexer import regular_expression as re
from lexer import syntax_tree as st
from lexer import afn
from lexer import automaton_operations as ao
from lexer import lexer_simulation as ls

from functools import reduce
from parser.grammar import Grammar
from parser.first_follow import compute_first, compute_follow, export_first_follow
from parser.lr0_items import canonical_collection, export_canonical_collection
from parser.slr_table import build_slr_table, export_slr_table
from parser.slr_parser import slr_parse_from_file

# Input and output files
INPUT_RE_FILE = "./input/example_input_RE.txt"
INPUT_USER_FILE = "./input/example_test_input.txt"
INPUT_GRAMMAR_FILE = "./input/example_input_grammar.txt"
OUTPUT_TOKEN_LIST_FILE = "./output/token_list_output.txt"
FIRST_FILE = "./output/first_output.txt"
FOLLOW_FILE = "./output/follow_output.txt"
STATES_FILE = "./output/lr0_states.txt"
TRANSITIONS_FILE = "./output/lr0_transitions.txt"
ACTION_FILE = "./output/slr_action_table.txt"
GOTO_FILE = "./output/slr_goto_table.txt"

ONLY_PARSER_MODE = False  # or True

def main():
    if not ONLY_PARSER_MODE:
        # ==============================================
        # Part I: Lexical analysis
        # ==============================================
        log_step("Starting regular expression to AFD conversion...")

        regular_expressions = []
        with open(INPUT_RE_FILE, 'r', encoding='utf-8') as file:
            for line_number, line in enumerate(file, start=1):
                line = line.strip()
                if line:
                    log_step(f"     Parsing regEx {line_number}: {line}")
                    regular_expressions.append(re.RegularExpression.from_definition_line(line))

        names = []
        afns = []
        for i, regex in enumerate(regular_expressions):
            names.append(regex.name)

            log_step("#1. Tokenize and create postfix format for regular expression")
            postfix = regex.to_postfix(regex.pattern)

            log_step("#2. Build syntax tree")
            tree = st.SyntaxTree(postfix)
            root = tree.build_syntax_tree()

            log_step("#3. Computing nullable, firstpos, lastpos, and followpos")
            followpos = tree.compute_nullable_first_last_follow(root)

            log_step("#4. Build AFD")
            afd = st.build_afd(root, followpos, tree.leaf_positions)
            afd.export_to_txt(f"./output/afd_output_{i}.txt")
            log_done(f"./output/afd_output_{i}.txt")

        for i, name in enumerate(names):
            afns.append(afn.AFN.load_afd_from_file(f"./output/afd_output_{i}.txt", token_type=name))

        log_step("#5. Union with epsilon transitions")
        union_afn = reduce(lambda a1, a2: ao.AutomatonOperations.union(a1, a2), afns)
        afd, token_map = union_afn.to_afd()

        log_step("#6. Lexer Analysis")
        ls.run_lexer(afd, token_map, INPUT_USER_FILE, OUTPUT_TOKEN_LIST_FILE)
        log_done(OUTPUT_TOKEN_LIST_FILE)


    # ==============================================
    # Part II: build SLR Parser
    # ==============================================
    log_step("#7. Interpret grammar")
    grammar = Grammar()
    grammar.load_grammar(INPUT_GRAMMAR_FILE)

    log_step("#8. Calculate FIRST and FOLLOW sets")
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)

    export_first_follow(first, follow, FIRST_FILE, FOLLOW_FILE)
    log_done(FIRST_FILE)
    log_done(FOLLOW_FILE)

    log_step("#9. Build set of LR(0) items (Closure & Goto)")
    states, transitions = canonical_collection(grammar)

    export_canonical_collection(states, transitions, STATES_FILE, TRANSITIONS_FILE)
    log_done(STATES_FILE)
    log_done(TRANSITIONS_FILE)

    log_step("#10. Build SLR parsing table")
    action_table, goto_table = build_slr_table(grammar, states, transitions, first, follow)

    export_slr_table(action_table, goto_table, ACTION_FILE, GOTO_FILE)
    log_done(ACTION_FILE)
    log_done(GOTO_FILE)

    # ==============================================
    # Part III: Execute Parser
    # ==============================================
    log_step("#11. Run SLR parsing")

    result = slr_parse_from_file(OUTPUT_TOKEN_LIST_FILE, action_table, goto_table)

    if result:
        print("Sentence Accepted!")
    else:
        print("Sentence Rejected!")


# ==============================================
# Utility log methods
# ==============================================

def log_step(msg):
    print(f"\n {msg}\n")


def log_success(msg):
    print(f" {msg}\n")


def log_done(file):
    print(f" File saved: {file}\n")


if __name__ == "__main__":
    main()