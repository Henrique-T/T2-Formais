

def simulate_dfa_on_text(dfa, token_map, text):
    """
    Simulates a DFA over an entire input text, returning a list of recognized tokens.

    This function:
    - Traverses the input string using the DFA transitions.
    - Tracks the last accepting state to ensure maximal munch (longest match).
    - Associates each recognized lexeme with its corresponding token.
    - If no accepting state is found, it marks the lexeme as an error.

    Parameters:
        dfa: An object with attributes:
            - start_state: initial DFA state
            - transitions: dict[state][symbol] -> next_state
            - accept_states: set of accepting states
        token_map: dict mapping DFA states to token names
        text (str): the complete input program as a single string

    Returns:
        List[Tuple[str, str]]: A list of (lexeme, token) tuples, where token is either a valid name or "erro!".
    """
    i = 0
    tokens = []

    while i < len(text):
        state = dfa.start_state
        last_accepting = None
        last_accepting_index = i
        current_index = i

        while current_index < len(text):
            symbol = text[current_index]
            #print(f"Reading symbol: '{symbol}' from state {state}")

            if symbol not in dfa.transitions.get(state, {}):
                print(f" No transition for symbol '{symbol}' from state {state}")
                break

            state = dfa.transitions[state][symbol]
            #print(f"Transition to state {state}")

            if state in dfa.accept_states:
                last_accepting = state
                last_accepting_index = current_index + 1

            current_index += 1

        if last_accepting is not None:
            lexeme = text[i:last_accepting_index]

            token = None
            for substate in sorted(last_accepting):
                if substate in token_map:
                    token = token_map[substate]
                    break

            if token is None:
                token = "erro!"

            tokens.append((lexeme, token))
            i = last_accepting_index
        else:
            tokens.append((text[i], "erro!"))
            i += 1

    return tokens

def simulate_dfa_on_line(dfa, token_map, line):
    """
    Simulates DFA execution over a single line of input.

    This function:
    - Verifies whether the DFA fully accepts the given line.
    - Resolves the token based on the final accepting state.
    - If no valid path exists or final state is not accepting, returns "erro!".

    Parameters:
        dfa: An object with attributes:
            - start_state
            - transitions: dict[state][symbol] -> next_state
            - accept_states: set of accepting states
        token_map: dict mapping DFA sub-states to token names
        line (str): a single line of input

    Returns:
        Tuple[str, str]: (line, token) if accepted; otherwise (line, "erro!")
    """
    escaped_symbol_map = {
        '+': r'\+',
        '-': r'\-',
        '*': r'\*',
        '/': r'\/',
        '(': r'\(',
        ')': r'\)',
        '[': r'\[',
        ']': r'\]',
        '\\': r'\\',
    }

    state = dfa.start_state
    i = 0
    while i < len(line):
        symbol = line[i]
        escaped_symbol = escaped_symbol_map.get(symbol, symbol)

        if escaped_symbol not in dfa.transitions.get(state, {}):
            return (line, "erro!")
        state = dfa.transitions[state][escaped_symbol]
        i += 1

    if state in dfa.accept_states:
        substates = state if isinstance(state, frozenset) else frozenset([state])
        token = None
        for substate in sorted(substates):
            if substate in token_map:
                token = token_map[substate]
                break
        return (line, token or "erro!")
    else:
        return (line, "erro!")

def run_lexer(dfa, token_map, input_text_path, output_token_path):
    """
    Runs the lexer using the DFA on an input file and writes token output to another file.

    This function:
    - Reads and strips lines from the input text file.
    - Simulates DFA execution line by line.
    - Writes results in the format <lexeme, token> per line in the output file.

    Parameters:
        dfa: The DFA used for simulation, with start_state, transitions, and accept_states.
        token_map: dict mapping DFA states or substates to token names.
        input_text_path (str): path to the input file containing program text.
        output_token_path (str): path to the output file where results will be written.
    """
    with open(input_text_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    tokens = []
    for line in lines:
        result = simulate_dfa_on_line(dfa, token_map, line)
        tokens.append(result)

    with open(output_token_path, 'w') as out:
        for lexeme, token in tokens:
            out.write(f"<{lexeme}, {token}>\n")