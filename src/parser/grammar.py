

import re


class Grammar:
    def __init__(self):
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None
        self.productions = []  # List of tuples (lhs, rhs) where rhs is a list of symbols

    def load_grammar(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Ignore empty lines and comments

            # Expected format: A ::= B C | D E
            if '::=' not in line:
                raise ValueError(f"Syntax error in line: {line}")

            lhs, rhs_part = line.split('::=')
            lhs = lhs.strip()
            rhs_alternatives = [alt.strip().split() for alt in rhs_part.strip().split('|')]

            # Set start symbol
            if self.start_symbol is None:
                self.start_symbol = lhs

            # Register non-terminal
            self.non_terminals.add(lhs)

            # Add productions
            for rhs in rhs_alternatives:
                self.productions.append((lhs, rhs))

        self._infer_terminals()

    def _infer_terminals(self):
        symbols_rhs = set()
        for _, rhs in self.productions:
            symbols_rhs.update(rhs)
        self.terminals = symbols_rhs - self.non_terminals

    def print_grammar(self):
        print(f"Start Symbol: {self.start_symbol}")
        print(f"Non-Terminals: {self.non_terminals}")
        print(f"Terminals: {self.terminals}")
        print("Productions:")
        for lhs, rhs in self.productions:
            print(f"  {lhs} ::= {' '.join(rhs)}")
        print("")
