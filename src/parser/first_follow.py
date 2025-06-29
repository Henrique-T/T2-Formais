from collections import defaultdict

def compute_first(grammar):
    """
    Compute the FIRST set for each symbol in the grammar.
    FIRST(X) is the set of terminals that begin the strings derivable from X.
    """
    first = defaultdict(set)

    # Step 1: Terminals have themselves as their FIRST set
    for terminal in grammar.terminals:
        first[terminal].add(terminal)

    # Step 2: Initialize non-terminals with empty FIRST sets
    for non_terminal in grammar.non_terminals:
        first[non_terminal] = set()

    changed = True
    while changed:
        changed = False

        for lhs, rhs in grammar.productions:
            old_size = len(first[lhs])

            if not rhs or rhs == ['ε']:
                # If production is empty or epsilon, add ε to FIRST(lhs)
                first[lhs].add('ε')
            else:
                # Process symbols from left to right
                nullable_prefix = True
                for symbol in rhs:
                    # Add FIRST(symbol) excluding ε
                    first[lhs].update(first[symbol] - {'ε'})

                    # Stop if symbol is not nullable
                    if 'ε' not in first[symbol]:
                        nullable_prefix = False
                        break

                # If all symbols in rhs are nullable, add ε to FIRST(lhs)
                if nullable_prefix:
                    first[lhs].add('ε')

            # If FIRST(lhs) changed, another iteration is needed
            if len(first[lhs]) > old_size:
                changed = True

    return dict(first)


def compute_follow(grammar, first):
    """
    Compute the FOLLOW set for each non-terminal in the grammar.
    FOLLOW(A) is the set of terminals that can appear immediately to the right of A.
    """
    follow = defaultdict(set)
    follow[grammar.start_symbol].add('$')  # Start symbol always has $ in its FOLLOW set

    changed = True
    while changed:
        changed = False

        for lhs, rhs in grammar.productions:
            trailer = follow[lhs].copy()  # What can follow the entire RHS

            for symbol in reversed(rhs):  # Iterate from right to left
                if symbol in grammar.non_terminals:
                    before = len(follow[symbol])
                    follow[symbol].update(trailer)
                    after = len(follow[symbol])

                    if after > before:
                        changed = True

                    # If symbol is nullable, trailer continues to grow
                    if 'ε' in first[symbol]:
                        trailer.update(first[symbol] - {'ε'})
                    else:
                        trailer = first[symbol]
                else:
                    # If symbol is a terminal, it becomes the new trailer
                    trailer = first[symbol] if symbol in first else {symbol}

    return dict(follow)


def export_first_follow(first, follow, first_file="./output/first_output.txt", follow_file="./output/follow_output.txt"):
    """
    Export FIRST and FOLLOW sets to separate text files for inspection.
    """
    with open(first_file, 'w', encoding='utf-8') as f:
        f.write("FIRST SETS\n===========\n\n")
        for symbol, values in first.items():
            f.write(f"FIRST({symbol}) = {sorted(values)}\n")
    print(f"FIRST saved to {first_file}")

    with open(follow_file, 'w', encoding='utf-8') as f:
        f.write("FOLLOW SETS\n============\n\n")
        for symbol, values in follow.items():
            f.write(f"FOLLOW({symbol}) = {sorted(values)}\n")
    print(f"FOLLOW saved to {follow_file}")
