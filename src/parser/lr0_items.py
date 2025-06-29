from collections import defaultdict

def closure(items, grammar):
    """
    Computes the closure of a set of LR(0) items for a given grammar.

    Parameters:
    - items: a set of items (lhs, rhs, dot_pos)
    - grammar: Grammar object

    Returns:
    - closure_set: a set containing the closure of the given items
    """
    closure_set = set(items)
    changed = True

    while changed:
        changed = False
        new_items = set()

        for item in closure_set:
            lhs, rhs, dot_pos = item

            # If the dot is before a non-terminal, expand its productions
            if dot_pos < len(rhs):
                symbol = rhs[dot_pos]
                if symbol in grammar.non_terminals:
                    for prod_lhs, prod_rhs in grammar.productions:
                        if prod_lhs == symbol:
                            new_item = (prod_lhs, tuple(prod_rhs), 0)
                            if new_item not in closure_set:
                                new_items.add(new_item)

        if new_items:
            closure_set.update(new_items)
            changed = True

    return closure_set


def goto(items, symbol, grammar):
    """
    Computes the GOTO set from a state (items) on a given symbol.

    Parameters:
    - items: current set of items (state)
    - symbol: grammar symbol (terminal or non-terminal)
    - grammar: Grammar object

    Returns:
    - set of items resulting from the GOTO operation
    """
    goto_set = set()

    for item in items:
        lhs, rhs, dot_pos = item
        # Shift the dot over the symbol if it matches
        if dot_pos < len(rhs) and rhs[dot_pos] == symbol:
            new_item = (lhs, rhs, dot_pos + 1)
            goto_set.add(new_item)

    return closure(goto_set, grammar) if goto_set else set()


def canonical_collection(grammar):
    """
    Constructs the canonical collection of LR(0) items (states) for a given grammar.

    Parameters:
    - grammar: Grammar object (will be modified with augmented production)

    Returns:
    - states: list of LR(0) item sets (states)
    - transitions: dictionary mapping (state, symbol) -> next_state
    """
    states = []
    transitions = {}

    # Augment the grammar by adding a new start symbol
    augmented_start = grammar.start_symbol + "'"
    while augmented_start in grammar.non_terminals:
        augmented_start += "'"

    augmented_production = (augmented_start, [grammar.start_symbol])
    grammar.productions = [augmented_production] + grammar.productions
    grammar.non_terminals.add(augmented_start)
    grammar.start_symbol = augmented_start

    # Initialize the first state with the augmented production
    start_item = (augmented_start, tuple([grammar.productions[0][1][0]]), 0)
    start_state = closure({start_item}, grammar)
    states.append(start_state)

    added = True
    while added:
        added = False
        new_states = []

        for state in states:
            symbols = set()
            # Find all symbols that appear after the dot in the state
            for item in state:
                lhs, rhs, dot_pos = item
                if dot_pos < len(rhs):
                    symbols.add(rhs[dot_pos])

            # Compute transitions for each symbol
            for symbol in symbols:
                target = goto(state, symbol, grammar)

                if not target:
                    continue

                if target not in states and target not in new_states:
                    new_states.append(target)
                    transitions[(frozenset(state), symbol)] = frozenset(target)
                    added = True
                else:
                    # Reuse existing state index if already created
                    for idx, s in enumerate(states + new_states):
                        if s == target:
                            transitions[(frozenset(state), symbol)] = frozenset(s)

        states.extend(new_states)

    return states, transitions


def export_canonical_collection(states, transitions,
                                states_file,
                                transitions_file):
    """
    Exports the canonical LR(0) states and transitions to text files.

    Parameters:
    - states: list of LR(0) states
    - transitions: dictionary of transitions
    - states_file: output path for states
    - transitions_file: output path for transitions
    """
    with open(states_file, 'w', encoding='utf-8') as f:
        f.write("LR(0) STATES\n============\n\n")
        for idx, state in enumerate(states):
            f.write(f"State {idx}:\n")
            for item in state:
                lhs, rhs, dot = item
                rhs_with_dot = list(rhs)
                rhs_with_dot.insert(dot, '•')  # Insert the dot in the correct position
                f.write(f"  {lhs} → {' '.join(rhs_with_dot)}\n")
            f.write("\n")

    with open(transitions_file, 'w', encoding='utf-8') as f:
        f.write("TRANSITIONS\n===========\n\n")
        for (from_state, symbol), to_state in transitions.items():
            from_idx = states.index(set(from_state))
            to_idx = states.index(set(to_state))
            f.write(f"  State {from_idx} -- {symbol} --> State {to_idx}\n")
