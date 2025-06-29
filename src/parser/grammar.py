import re

class Grammar:
    def __init__(self):
        # Set of non-terminal symbols (e.g., E, T, F)
        self.non_terminals = set()
        # Set of terminal symbols (e.g., id, +, *, etc.)
        self.terminals = set()
        # The start symbol of the grammar
        self.start_symbol = None
        # List of productions as tuples: (lhs, rhs) where rhs is a list of symbols
        self.productions = []

    def load_grammar(self, filename):
        """
        Loads grammar rules from a file.
        Format: A ::= B C | D E
        Ignores blank lines and comments (lines starting with #).
        """
        with open(filename, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Skip comments and empty lines

            if '::=' not in line:
                raise ValueError(f"Syntax error in line: {line}")

            # Split into LHS and RHS of the production
            lhs, rhs_part = line.split('::=')
            lhs = lhs.strip()

            # Split RHS alternatives by '|', then split each alternative into symbols
            rhs_alternatives = [alt.strip().split() for alt in rhs_part.strip().split('|')]

            # Set the first non-terminal encountered as the start symbol
            if self.start_symbol is None:
                self.start_symbol = lhs

            # Register LHS as a non-terminal
            self.non_terminals.add(lhs)

            # Add each alternative as a separate production
            for rhs in rhs_alternatives:
                self.productions.append((lhs, rhs))

        # Infer terminals after reading all productions
        self._infer_terminals()

    def _infer_terminals(self):
        """
        Infers terminal symbols by collecting all RHS symbols and
        removing those that are non-terminals.
        """
        symbols_rhs = set()
        for _, rhs in self.productions:
            symbols_rhs.update(rhs)

        # Terminals are all symbols that appear in RHS but are not non-terminals
        self.terminals = symbols_rhs - self.non_terminals

    def print_grammar(self):
        """
        Prints the grammar components: start symbol, non-terminals,
        terminals, and production rules.
        """
        print(f"Start Symbol: {self.start_symbol}")
        print(f"Non-Terminals: {self.non_terminals}")
        print(f"Terminals: {self.terminals}")
        print("Productions:")
        for lhs, rhs in self.productions:
            print(f"  {lhs} ::= {' '.join(rhs)}")
        print("")