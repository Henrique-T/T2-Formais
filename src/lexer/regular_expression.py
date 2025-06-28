import re as re_

class RegularExpression:
    """
    Represents a regular expression definition and provides utilities for processing and transforming it.

    This class supports parsing named regular expressions from a definition line,
    expanding character classes, inserting explicit concatenation symbols, and converting
    infix regular expressions to postfix (Reverse Polish Notation) format.

    Attributes:
        name (str): The name or identifier of the regular expression.
        pattern (str): The raw or preprocessed infix pattern of the regular expression.
    """
    def __init__(self, name: str, pattern: str):
        self.name = name
        self.pattern = pattern.strip()
    
    def __repr__(self):
        """
        Returns a string representation of the RegularExpression instance.

        Returns:
            str: A formatted string for debugging and logging.
        """
        return f"<RegularExpression name='{self.name}' pattern='{self.pattern}'>"

    @staticmethod
    def from_definition_line(line: str):
        """
        Creates a RegularExpression instance from a definition line in the format "name: pattern".

        Args:
            line (str): A string containing the name and pattern separated by a colon.

        Returns:
            RegularExpression: A new RegularExpression instance.

        Raises:
            ValueError: If the line does not contain a colon.

        RE e.g.: 'id: [a-zA-Z]([a-zA-Z] | [0-9])*'
        """
        if ':' not in line:
            raise ValueError(f"Invalid regular expression definition: {line}")
        name, pattern = line.split(':', 1)
        return RegularExpression(name.strip(), pattern.strip())
    
    @staticmethod
    def is_operator(c):
        return c in {'|', '.', '*', '+', '?'} and not (c.startswith('\\') and len(c) == 2)
    
    def is_operand(token):
        return (
            (token.startswith('[') and token.endswith(']'))  # character class
            or token.isalnum()  # single letter/digit
        )

    @staticmethod
    def precedence(op):
        if op in {'*', '+', '?'}:
            return 3
        elif op == '.':
            return 2
        elif op == '|':
            return 1
        return 0
    
    def starts_expr(token):
        return token in {'(',} or token.startswith('[') or token.isalnum()

    def add_concatenation_symbols(self, pattern):
        """
        Inserts explicit concatenation symbols '.' into the regular expression pattern
        where implicit concatenation is intended.

        Args:
            pattern (str): The input infix pattern string.

        Returns:
            str: The updated pattern with '.' for concatenation.
        """
        i = 0

        def is_character_class(token):
            return len(token) >= 3 and token[0] == '[' and token[-1] == ']'

        def is_literal(token):
            return (len(token) == 1 and token.isalnum()) or token.startswith('\\')

        def is_operand(token):
            return (
                is_character_class(token)
                or is_literal(token)
                or token == ')'
                or (token.startswith('\\') and len(token) == 2)
            )

        def is_prefix(token):
            return token in ['*', '+', '?'] or (token.startswith('\\') and token[1] in {'*', '+', '?'})

        def is_open_group(token):
            return token == '('

        def is_closing_group(token):
            return token == ')'

        def read_token():
            nonlocal i
            if pattern[i] == '\\':
                if i + 1 < len(pattern):
                    token = pattern[i:i+2]
                    i += 2
                else:
                    token = pattern[i]
                    i += 1
            elif pattern[i] == '[':
                j = i + 1
                while j < len(pattern) and pattern[j] != ']':
                    j += 1
                token = pattern[i:j + 1]
                i = j + 1
            else:
                token = pattern[i]
                i += 1
            return token

        tokens = []
        while i < len(pattern):
            tokens.append(read_token())

        output = []
        for j in range(len(tokens)):
            token = tokens[j]
            output.append(token)

            # Lookahead to decide if we should insert a concatenation
            if j + 1 < len(tokens):
                curr = token
                next_tok = tokens[j + 1]

                if (
                    (is_operand(curr) or is_closing_group(curr) or is_prefix(curr))
                    and (is_operand(next_tok) or is_open_group(next_tok))
                    and curr != '|'
                    and next_tok not in {'|', '*', '+', '?', ')'}
                ):
                    output.append('.')

        self.pattern = ''.join(output)
        transformed = ''.join(output)
        return transformed
    
    def to_postfix(self, pattern):
        """
        Converts an infix regular expression pattern to postfix notation (Reverse Polish Notation),
        adding explicit concatenation and expanding character classes.

        Args:
            pattern (str): The infix pattern string.

        Returns:
            List[str]: A list of tokens representing the postfix expression.
        """
        pattern = self.add_concatenation_symbols(self.expand_character_classes(pattern))
        output = []
        stack = []
        for token in self.tokenize(pattern):
            if token == '(':
                stack.append(token)
            elif token == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                stack.pop()  # pop '('
            elif self.is_operator(token):
                while (stack and stack[-1] != '(' and
                       ((self.precedence(token) < self.precedence(stack[-1])) or
                        (self.precedence(token) == self.precedence(stack[-1]) and token != '*'))):
                    output.append(stack.pop())
                stack.append(token)
            else:
                output.append(token)
        while stack:
            output.append(stack.pop())
        output.append('#')
        output.append('.')  # <- final concat
        # print("RegEx to Postfix: ")
        # print(output)
        # print("")
        return output

    def expand_character_classes(self, pattern):
        """
        Expands character classes (e.g., [a-z]) into explicit alternation format (e.g., (a|b|...|z)).

        Args:
            pattern (str): The pattern containing character classes.

        Returns:
            str: The pattern with expanded character classes.
        """
        def expand_class(match):
            chars = []
            content = match.group(1)
            i = 0
            while i < len(content):
                if i + 2 < len(content) and content[i+1] == '-':
                    start, end = content[i], content[i+2]
                    chars.extend([chr(c) for c in range(ord(start), ord(end)+1)])
                    i += 3
                else:
                    chars.append(content[i])
                    i += 1
            return '(' + '|'.join(chars) + ')'
        return re_.sub(r'\[([^\]]+)\]', expand_class, pattern) #TODO: replace re_.sub() for my own method.
    
    def tokenize(self, pattern):
        """
        Splits the regular expression string into a list of tokens, treating operators,
        parentheses, and literals separately.

        Args:
            pattern (str): The regular expression string with explicit operators.

        Returns:
            List[str]: A list of tokens extracted from the pattern.
        """
        tokens = []
        i = 0
        while i < len(pattern):
            if pattern[i] == '\\':
                if i + 1 < len(pattern):
                    tokens.append('\\' + pattern[i + 1])  # escaped character, like '\*'
                    i += 2
                else:
                    tokens.append('\\')  # lone backslash (syntax error?)
                    i += 1
            elif pattern[i] in {'(', ')', '|', '*', '+', '?', '.'}:
                tokens.append(pattern[i])
                i += 1
            elif not pattern[i].isspace():
                tokens.append(pattern[i])
                i += 1
            else:
                i += 1
        return tokens