from collections import deque
from lexer import afd

class AFN:
    """
    Represents a Non-deterministic Finite Automaton (AFN/NFA), including ε-transitions.

    Attributes:
        states (set[int]): Set of all states.
        start_state (int): The start state of the AFN.
        final_states (set[int]): Set of accepting (final) states.
        transitions (dict[int][str] -> set[int]): State transition function including ε-transitions.
        alphabet (set[str]): Set of valid input symbols (excluding ε unless used explicitly).
        token_types (dict[int] -> str): Optional mapping from final states to token types.
    """
    def __init__(self, states, start_state, final_states, transitions, alphabet, token_types=None):
        self.states = states
        self.start_state = start_state
        self.final_states = final_states
        self.transitions = transitions
        self.alphabet = alphabet
        self.token_types = token_types or {}

    def offset_states(self, offset):
        """
        Returns a new AFN where all state numbers are offset by a given value.

        Useful for merging multiple AFNs while avoiding state number conflicts.

        Args:
            offset (int): The value to add to all state identifiers.

        Returns:
            AFN: A new AFN instance with updated state identifiers.
        """
        new_states = {s + offset for s in self.states}
        new_start = self.start_state + offset
        new_finals = {s + offset for s in self.final_states}

        new_transitions = {}
        for state, trans in self.transitions.items():
            new_state = state + offset
            new_transitions[new_state] = {}
            for symbol, destinations in trans.items():
                new_transitions[new_state][symbol] = {d + offset for d in destinations}

        new_token_types = {s + offset: t for s, t in self.token_types.items()}
        return AFN(new_states, new_start, new_finals, new_transitions, self.alphabet, new_token_types)


    @staticmethod
    def load_afd_from_file(filepath, token_type=None):
        """
        Loads an AFN from a file that was exported in AFD format.

        Args:
            filepath (str): Path to the input file.
            token_type (str, optional): Token type to associate with all final states.

        Returns:
            AFN: A new AFN instance reconstructed from the file.
        """
        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        start_state = int(lines[1])
        final_states = {int(s) for s in lines[2].split(',')}
        alphabet = set(lines[3].split(','))
        transitions = {}

        for line in lines[4:]:
            src, symbol, dest = line.split(',')
            src = int(src)
            dest = int(dest)
            if src not in transitions:
                transitions[src] = {}
            if symbol not in transitions[src]:
                transitions[src][symbol] = set()
            transitions[src][symbol].add(dest)

        states = set(transitions.keys())
        for dests in transitions.values():
            for dest_set in dests.values():
                states.update(dest_set)

        token_types = {}
        if token_type:
            for s in final_states:
                token_types[s] = token_type

        return AFN(states, start_state, final_states, transitions, alphabet, token_types)

    def __str__(self):
        """Returns a human-readable string representation of the AFN."""
        result = []
        result.append(f"States: {sorted(self.states)}")
        result.append(f"Start state: {self.start_state}")
        result.append(f"Accept states: {sorted(self.final_states)}")
        result.append(f"Alphabet: {sorted(self.alphabet)}")
        result.append("Transitions:")
        for state, trans_dict in self.transitions.items():
            for symbol, destinations in trans_dict.items():
                for dest in destinations:
                    result.append(f"  {state} -- {symbol} --> {dest}")
        return "\n".join(result)

    def to_afd(self):
        """
        Converts this AFN (with possible ε-transitions) to an equivalent AFD (DFA).

        Returns:
            tuple:
                - AFD: The deterministic equivalent of the current AFN.
                - dict[int] -> str: Mapping of DFA state IDs to token types.
        """
        def epsilon_closure(states):
            """Compute the epsilon-closure of a set of states."""
            closure = set(states)
            stack = list(states)
            while stack:
                state = stack.pop()
                for dest in self.transitions.get(state, {}).get('ε', set()):
                    if dest not in closure:
                        closure.add(dest)
                        stack.append(dest)
            return closure

        def move(states, symbol):
            """Compute the set of states reachable from 'states' via 'symbol'."""
            result = set()
            for state in states:
                if symbol in self.transitions.get(state, {}):
                    result.update(self.transitions[state][symbol])
            return result

        # Initial ε-closure
        start_closure = frozenset(epsilon_closure({self.start_state}))
        queue = deque([start_closure])
        visited = {start_closure}
        transitions = {}
        accept_states = set()

        # Mapping frozensets to integer IDs for table representation
        state_id_map = {start_closure: 0}
        id_counter = 1

        lexical_table = []  # Each entry: (state_id, symbol, next_state_id)

        while queue:
            current = queue.popleft()
            if current not in transitions:
                transitions[current] = {}

            current_id = state_id_map[current]

            for symbol in self.alphabet:
                if symbol == 'ε':
                    continue
                target = frozenset(epsilon_closure(move(current, symbol)))
                if not target:
                    continue
                if target not in visited:
                    visited.add(target)
                    queue.append(target)
                    state_id_map[target] = id_counter
                    id_counter += 1

                transitions[current][symbol] = target
                target_id = state_id_map[target]

                # Add transition to lexical analysis table
                lexical_table.append((current_id, symbol, target_id))

        # Mark accept states
        for state in visited:
            if any(s in self.final_states for s in state):
                accept_states.add(state)

        # Print lexical analysis table
        # print("Lexical Analysis Table:")
        # print(f"{'From':>5} {'Symbol':>10} {'To':>5}")
        # for from_id, symbol, to_id in lexical_table:
        #     print(f"{from_id:>5} {symbol:>10} {to_id:>5}")

        token_map = {}  # NFA state -> token_type

        for nfa_state in self.final_states:
            if nfa_state in self.token_types:
                token_map[nfa_state] = self.token_types[nfa_state]

        return afd.AFD(
            start_state=start_closure,
            accept_states=accept_states,
            transitions=transitions,
            token_map=token_map
        ), token_map



