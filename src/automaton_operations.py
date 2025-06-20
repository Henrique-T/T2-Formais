import afn

class AutomatonOperations:
    """
    Provides static operations for combining and manipulating finite automata (AFNs/NFAs).

    Currently supports:
        - Union of two AFNs
    """
    @staticmethod
    def union(afn1: afn.AFN, afn2: afn.AFN) -> afn.AFN:
        """
        Constructs a new AFN representing the union of two given AFNs.

        This operation:
            - Offsets states in the second AFN to avoid naming collisions.
            - Creates a new start state with ε-transitions to the original start states.
            - Merges transitions, states, final states, and alphabets.
            - Preserves token types from both automata.

        Args:
            afn1 (AFN): The first AFN.
            afn2 (AFN): The second AFN.

        Returns:
            AFN: A new AFN that accepts the union of the languages of `afn1` and `afn2`.
        """
        # Offset afn2 states to avoid collision
        offset = max(afn1.states) + 1
        afn2 = afn2.offset_states(offset)

        # Create new start state
        new_start = max(afn2.states) + 1
        new_states = afn1.states | afn2.states | {new_start}
        new_finals = afn1.final_states | afn2.final_states
        new_alphabet = afn1.alphabet | afn2.alphabet

        # Merge transitions
        new_transitions = {**afn1.transitions}
        for state, trans in afn2.transitions.items():
            if state not in new_transitions:
                new_transitions[state] = {}
            for symbol, dests in trans.items():
                if symbol not in new_transitions[state]:
                    new_transitions[state][symbol] = set()
                new_transitions[state][symbol].update(dests)

        # Add epsilon transitions from new start to both automata
        if new_start not in new_transitions:
            new_transitions[new_start] = {}
        new_transitions[new_start]['ε'] = {afn1.start_state, afn2.start_state}
        
        new_token_types = {**afn1.token_types, **afn2.token_types}
        return afn.AFN(new_states, new_start, new_finals, new_transitions, new_alphabet | {'ε'}, new_token_types)


