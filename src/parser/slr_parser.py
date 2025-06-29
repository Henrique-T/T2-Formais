from collections import defaultdict


class SymbolTable:
    def __init__(self, reserved_words=None):
        self.symbols = {}  # {lexeme: (index, category)}
        self.counter = 1
        self.reserved_words = reserved_words or {}  # e.g., {'for': 'PR', 'if': 'PR'}

    def add_or_get(self, lexeme):
        if lexeme in self.symbols:
            return self.symbols[lexeme]  # return (index, category)
        else:
            category = self.reserved_words.get(lexeme, 'ID')
            self.symbols[lexeme] = (self.counter, category)
            self.counter += 1
            return self.symbols[lexeme]

    def __str__(self):
        result = "\n------ Symbol Table ------\n"
        for lex, (idx, cat) in sorted(self.symbols.items(), key=lambda x: x[1][0]):
            result += f"{idx}: {lex} ({cat})\n"
        return result



def load_tokens_from_file(file_path):
    """
    Read file token_list_output.txt and returns a list of tokens in the following format:
    [('a1', 'id'), ('0', 'erro!'), ...]
    """
    TOKEN_REMAP = {
        'plus': '+',
        'times': '*',
        'lpar': '(',
        'rpar': ')',
        'minus': '-',
        'div': '/',
    }

    tokens = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line or not line.startswith('<') or not line.endswith('>'):
                continue  # ignore invalid lines
            content = line[1:-1]  # Remove <>
            parts = content.split(',')

            if len(parts) != 2:
                continue  # ignore poorly formatted lines

            lexeme = parts[0].strip()
            token_type = parts[1].strip()
            token_type = TOKEN_REMAP.get(token_type, token_type)  # remap token names
            tokens.append((lexeme, token_type))
    return tokens


def slr_parse_from_file(file_path, action_table, goto_table):
    """
    Execute SLR parser reading tokens from file and updates symbol table.
    """
    token_list = load_tokens_from_file(file_path)

    print("Tokens loaded:")
    for lexeme, token_type in token_list:
        print(f"Lexeme: '{lexeme}', Token type: '{token_type}'")

    # Verifica erros léxicos
    error_tokens = [t for t in token_list if t[1] == 'erro!']
    if error_tokens:
        print("Lexical error found! Invalid tokens:")
        for lexeme, _ in error_tokens:
            print(f"  -> {lexeme}")
        print("Sentence rejected!")
        return False

    input_tokens = token_list + [('$', '$')]  # Adds EOF

    stack = [0]
    pointer = 0
    output_steps = []
    
    reserved_words = {
    'for': 'PR',
    'if': 'PR',
    'else': 'PR',
    'while': 'PR',
    'return': 'PR'
}
    symbol_table = SymbolTable(reserved_words=reserved_words)


    print("\n#11. Parse SLR tables\n")

    while True:
        state = stack[-1]
        current_token = input_tokens[pointer][1]  # Token pattern ('id', '+', 'num', etc.)
        lexeme = input_tokens[pointer][0]         # lexeme ('a1', '+', '21', etc.)

        action = action_table.get((state, current_token))

        if action is None:
            print(f"Syntax error! No actions for (state {state}, token '{current_token}').")
            print("Sentence Rejected!")
            print(symbol_table)
            return False

        if action[0] == 'shift':
            next_state = action[1]

            # # Atualiza a tabela de símbolos se for um identificador (id)
            # if current_token == 'id':
            #     index, category = symbol_table.add_or_get(lexeme)
            #     output_steps.append(f"Shift <{lexeme}, {category}({index})> and goes to state {next_state}")
            # else:
            #     output_steps.append(f"Shift '{current_token}' and goes to state {next_state}")
            # Atualiza a tabela de símbolos para qualquer lexema, usando palavras reservadas
            
            index, category = symbol_table.add_or_get(lexeme)
            output_steps.append(f"Shift <{lexeme}, {category}({index})> and goes to state {next_state}")



            stack.append(current_token)
            stack.append(next_state)
            pointer += 1

        elif action[0] == 'reduce':
            lhs, rhs = action[1]
            if rhs != ('ε',):
                pop_length = 2 * len(rhs)
                stack = stack[:-pop_length]
            state = stack[-1]
            stack.append(lhs)
            goto_state = goto_table.get((state, lhs))
            if goto_state is None:
                print(f"Goto error! no transition for (state {state}, non-terminal '{lhs}').")
                print("Sentence rejected!")
                print(symbol_table)
                return False
            stack.append(goto_state)
            output_steps.append(f"Reduce por {lhs} → {' '.join(rhs)}")

        elif action[0] == 'accept':
            output_steps.append("Accepts input!")
            for step in output_steps:
                print(step)
            print("\Sentence accepted!")
            print(symbol_table)
            return True

        else:
            print(f"Unknown action: {action}")
            print("Sentence rejected!")
            print(symbol_table)
            return False
