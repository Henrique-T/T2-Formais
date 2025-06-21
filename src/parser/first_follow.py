from collections import defaultdict


def compute_first(grammar):
    first = defaultdict(set)

    for terminal in grammar.terminals:
        first[terminal].add(terminal)

    for non_terminal in grammar.non_terminals:
        first[non_terminal] = set()

    changed = True
    while changed:
        changed = False

        for lhs, rhs in grammar.productions:
            before = len(first[lhs])

            if len(rhs) == 0 or rhs == ['ε']:
                first[lhs].add('ε')
            else:
                for symbol in rhs:
                    first[lhs].update(first[symbol] - {'ε'})
                    if 'ε' in first[symbol]:
                        continue
                    else:
                        break
                else:
                    first[lhs].add('ε')

            if len(first[lhs]) > before:
                changed = True

    return dict(first)


def compute_follow(grammar, first):
    follow = defaultdict(set)
    follow[grammar.start_symbol].add('$')

    changed = True
    while changed:
        changed = False

        for lhs, rhs in grammar.productions:
            trailer = follow[lhs].copy()

            for symbol in reversed(rhs):
                if symbol in grammar.non_terminals:
                    before = len(follow[symbol])
                    follow[symbol].update(trailer)
                    after = len(follow[symbol])
                    if after > before:
                        changed = True

                    if 'ε' in first[symbol]:
                        trailer.update(first[symbol] - {'ε'})
                    else:
                        trailer = first[symbol]
                else:
                    trailer = first[symbol] if symbol in first else {symbol}

    return dict(follow)


def export_first_follow(first, follow, first_file="./output/first_output.txt", follow_file="./output/follow_output.txt"):
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
