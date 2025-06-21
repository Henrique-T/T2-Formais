

import re


class Grammar:
    def __init__(self):
        self.non_terminals = set()
        self.terminals = set()
        self.start_symbol = None
        self.productions = []  # Lista de tuplas (lhs, rhs) onde rhs é uma lista de símbolos

    def load_grammar(self, filename):
        with open(filename, 'r') as file:
            lines = file.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Ignora linhas vazias ou comentários

            # Parse da linha no formato: A ::= B C D
            if '::=' not in line:
                raise ValueError(f"Erro de sintaxe na linha: {line}")

            lhs, rhs = line.split('::=')
            lhs = lhs.strip()
            rhs_symbols = rhs.strip().split()

            # Definir símbolo inicial
            if self.start_symbol is None:
                self.start_symbol = lhs

            # Adicionar não-terminal
            self.non_terminals.add(lhs)

            # Adicionar produção
            self.productions.append((lhs, rhs_symbols))

        # Inferir terminais
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
