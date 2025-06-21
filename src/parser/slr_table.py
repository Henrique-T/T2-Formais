def build_slr_table(grammar, states, transitions, first, follow):
    action_table = {}
    goto_table = {}

    for idx, state in enumerate(states):
        for item in state:
            lhs, rhs, dot = item

            if dot < len(rhs):
                symbol = rhs[dot]
                target = transitions.get((frozenset(state), symbol))

                if symbol in grammar.terminals and target:
                    target_idx = states.index(set(target))
                    action_table[(idx, symbol)] = ('shift', target_idx)

                elif symbol in grammar.non_terminals and target:
                    target_idx = states.index(set(target))
                    goto_table[(idx, symbol)] = target_idx

            elif dot == len(rhs) and lhs != grammar.start_symbol:
                for terminal in follow[lhs]:
                    action_table[(idx, terminal)] = ('reduce', (lhs, rhs))

            elif lhs == grammar.start_symbol and dot == len(rhs):
                action_table[(idx, '$')] = ('accept',)

    return action_table, goto_table


def export_slr_table(action_table, goto_table, action_file="./output/slr_action_table.txt", goto_file="./output/slr_goto_table.txt"):
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
