def build_slr_table(grammar, states, transitions, first, follow):
    """
    Builds the SLR parsing tables (ACTION and GOTO) for a given grammar.

    Parameters:
    - grammar: the grammar object (with productions, terminals, non-terminals, start symbol)
    - states: the canonical LR(0) item sets
    - transitions: dictionary mapping (state, symbol) → next_state
    - first: dictionary mapping symbols to their FIRST set
    - follow: dictionary mapping non-terminals to their FOLLOW set

    Returns:
    - action_table: a dict mapping (state, terminal) → ('shift', state) or ('reduce', production) or ('accept',)
    - goto_table: a dict mapping (state, non-terminal) → next_state
    """
    action_table = {}
    goto_table = {}

    for idx, state in enumerate(states):
        for item in state:
            lhs, rhs, dot = item

            # Case 1: Dot is before a symbol (potential shift)
            if dot < len(rhs):
                symbol = rhs[dot]
                target = transitions.get((frozenset(state), symbol))

                if symbol in grammar.terminals and target:
                    # If it's a terminal, add a shift action
                    target_idx = states.index(set(target))
                    action_table[(idx, symbol)] = ('shift', target_idx)

                elif symbol in grammar.non_terminals and target:
                    # If it's a non-terminal, add a goto transition
                    target_idx = states.index(set(target))
                    goto_table[(idx, symbol)] = target_idx

            # Case 2: Dot is at the end of a production (potential reduce)
            elif dot == len(rhs) and lhs != grammar.start_symbol:
                for terminal in follow[lhs]:
                    # Add reduce action for each terminal in FOLLOW(lhs)
                    action_table[(idx, terminal)] = ('reduce', (lhs, rhs))

            # Case 3: Accept condition (S' → S •)
            elif lhs == grammar.start_symbol and dot == len(rhs):
                action_table[(idx, '$')] = ('accept',)

    return action_table, goto_table


def export_slr_table(action_table, goto_table,
                     action_file="./output/slr_action_table.txt",
                     goto_file="./output/slr_goto_table.txt"):
    """
    Exports the ACTION and GOTO tables to human-readable text files.

    Parameters:
    - action_table: the ACTION parsing table
    - goto_table: the GOTO parsing table
    - action_file: file path to save the ACTION table
    - goto_file: file path to save the GOTO table
    """
    with open(action_file, 'w', encoding='utf-8') as f:
        f.write("ACTION TABLE\n============\n\n")
        for (state, symbol), action in sorted(action_table.items()):
            f.write(f"ACTION[{state}, {symbol}] = {action}\n")
    print(f"ACTION Table saved to {action_file}")

    with open(goto_file, 'w', encoding='utf-8') as f:
        f.write("GOTO TABLE\n==========\n\n")
        for (state, symbol), target in sorted(goto_table.items()):
            f.write(f"GOTO[{state}, {symbol}] = {target}\n")
    print(f"GOTO Table saved to {goto_file}")
