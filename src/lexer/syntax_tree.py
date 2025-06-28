from lexer import afd
from collections import deque, defaultdict

class SyntaxTree():
    """
    Constructs and analyzes the syntax tree of a regular expression in postfix notation.

    This class builds a syntax tree from postfix tokens of a regular expression, and computes
    nullable, firstpos, lastpos, and followpos sets required for the construction of a DFA
    using the syntax tree method.

    Attributes:
        stack (list): Temporary stack used for building the tree.
        postfix_tokens (list): Tokens in postfix notation representing the regular expression.
        leaf_positions (dict): Maps leaf node positions to their corresponding symbols.
    """
    def __init__(self, postfix_tokens):
        self.stack = []
        self.postfix_tokens = postfix_tokens
        self.leaf_positions = {}  # Mapeia posição -> símbolo

    def build_syntax_tree(self):
        """Constructs the syntax tree from the postfix tokens and returns the root node."""
        position_counter = 1
        for token in self.postfix_tokens:
            if token == '#' or (token.startswith('\\') and len(token) == 2) or token.isalnum():
                node = Leaf(token, position_counter)
                self.leaf_positions[position_counter] = token  # <-- adiciona isso
                position_counter += 1
                self.stack.append(node)
            elif token in ['*', '+', '?']:
                if len(self.stack) < 1:
                    raise ValueError("Invalid postfix expression: missing operand for unary operator")
                child = self.stack.pop()
                self.stack.append(UnaryNode(token, child))
            elif token in ['|', '.']:
                if len(self.stack) < 2:
                    raise ValueError("Invalid postfix expression: missing operands for binary operator")
                right = self.stack.pop()
                left = self.stack.pop()
                self.stack.append(BinaryNode(token, left, right))
            else:
                raise ValueError(f"Unknown token: {token}")

        if len(self.stack) != 1:
            raise ValueError("Invalid postfix expression")
        return self.stack[0]

    def log_syntax_tree(self, node, indent=0):
        """
        Recursively logs the syntax tree structure to the console.

        Args:
            node (Node): The current node of the syntax tree.
            indent (int): The current indentation level (used for formatting).
        """
        prefix = "    " * indent
        if isinstance(node, Leaf):
            print(f"{prefix}Leaf(symbol='{node.symbol}', position={node.position})")
        elif isinstance(node, UnaryNode):
            print(f"{prefix}UnaryNode(operator='{node.symbol}')")
            self.log_syntax_tree(node.child, indent + 1)
        elif isinstance(node, BinaryNode):
            print(f"{prefix}BinaryNode(operator='{node.symbol}')")
            self.log_syntax_tree(node.left, indent + 1)
            self.log_syntax_tree(node.right, indent + 1)
        else:
            print(f"{prefix}Unknown Node Type")


    def compute_nullable_first_last_follow(self, root):
        """Computes nullable, firstpos, lastpos, and followpos for all nodes in the tree starting from the given root node."""
        followpos = dict()

        def traverse(node):
            if isinstance(node, Leaf):
                node.nullable = False
                node.firstpos = {node.position}
                node.lastpos = {node.position}
                followpos[node.position] = set()

            elif isinstance(node, UnaryNode):
                traverse(node.child)

                if node.symbol == '*':
                    node.nullable = True
                    node.firstpos = node.child.firstpos
                    node.lastpos = node.child.lastpos
                    for p in node.lastpos:
                        followpos[p].update(node.firstpos)
                elif node.symbol == '+':
                    node.nullable = node.child.nullable
                    node.firstpos = node.child.firstpos
                    node.lastpos = node.child.lastpos
                    for p in node.lastpos:
                        followpos[p].update(node.firstpos)
                elif node.symbol == '?':
                    node.nullable = True
                    node.firstpos = node.child.firstpos
                    node.lastpos = node.child.lastpos

            elif isinstance(node, BinaryNode):
                traverse(node.left)
                traverse(node.right)

                if node.symbol == '.':
                    node.nullable = node.left.nullable and node.right.nullable
                    node.firstpos = node.left.firstpos if not node.left.nullable else node.left.firstpos | node.right.firstpos
                    node.lastpos = node.right.lastpos if not node.right.nullable else node.left.lastpos | node.right.lastpos

                    for p in node.left.lastpos:
                        followpos[p].update(node.right.firstpos)

                elif node.symbol == '|':
                    node.nullable = node.left.nullable or node.right.nullable
                    node.firstpos = node.left.firstpos | node.right.firstpos
                    node.lastpos = node.left.lastpos | node.right.lastpos

        traverse(root)
        return followpos

class Node:
    """
    Base class for nodes in the syntax tree of a regular expression.

    Attributes:
        symbol (str): The symbol represented by the node (operator or terminal).
        nullable (bool): Whether the subtree rooted at this node can derive the empty string.
        firstpos (set): Set of positions that can appear first in a string derived from this node.
        lastpos (set): Set of positions that can appear last in a string derived from this node.
    """
    def __init__(self, symbol):
        self.symbol = symbol
        self.nullable = False
        self.firstpos = set()
        self.lastpos = set()

class Leaf(Node):
    """
    Represents a leaf node in the syntax tree, corresponding to a terminal symbol.

    Inherits from:
        Node

    Attributes:
        symbol (str): The terminal symbol (character) this leaf represents.
        position (int): A unique position number assigned to the leaf for use in followpos calculations.
    """
    def __init__(self, symbol, position):
        super().__init__(symbol)
        self.position = position

class UnaryNode(Node):
    """
    Represents a unary operator node in the syntax tree (e.g., '*', '+', '?').

    Inherits from:
        Node

    Attributes:
        symbol (str): The unary operator.
        child (Node): The single child node of this unary operator.
    """
    def __init__(self, symbol, child):
        super().__init__(symbol)
        self.child = child

class BinaryNode(Node):
    """
    Represents a binary operator node in the syntax tree (e.g., concatenation '.', or alternation '|').

    Inherits from:
        Node

    Attributes:
        symbol (str): The binary operator.
        left (Node): The left operand subtree.
        right (Node): The right operand subtree.
    """
    def __init__(self, symbol, left, right):
        super().__init__(symbol)
        self.left = left
        self.right = right

def build_afd(root, followpos, leaf_positions):
    """
    Constructs a deterministic finite automaton (AFD) from a syntax tree using followpos information.

    Args:
        root (Node): The root of the syntax tree.
        followpos (dict): A dictionary mapping position integers to sets of follow positions.
        leaf_positions (dict): A dictionary mapping positions to their respective terminal symbols.

    Returns:
        AFD: An instance of the AFD class representing the deterministic finite automaton.

    Raises:
        ValueError: If the special terminal symbol '#' is not found in the leaf positions.
    """
    # find '#' position
    hash_position = None
    for pos, symbol in leaf_positions.items():
        if symbol == '#':
            hash_position = pos
            break

    if hash_position is None:
        raise ValueError("Character '#' not found in RE.")

    # initial state: root firstpos
    start_state = frozenset(root.firstpos)
    dstates = [start_state]
    unmarked_states = deque([start_state])
    transitions = {}
    accept_states = set()

    while unmarked_states:
        current = unmarked_states.popleft()
        transitions[current] = {}

        symbol_to_positions = defaultdict(set)

        for pos in current:
            symbol = leaf_positions[pos]
            if symbol == '#':
                continue  # ignorar o símbolo especial
            for follow in followpos.get(pos, []):
                symbol_to_positions[symbol].add(follow)

        for symbol, new_positions in symbol_to_positions.items():
            new_state = frozenset(new_positions)
            if new_state not in dstates:
                dstates.append(new_state)
                unmarked_states.append(new_state)
            transitions[current][symbol] = new_state

    for state in dstates:
        if hash_position in state:
            accept_states.add(state)

    return afd.AFD(start_state, accept_states, transitions)

def find_leaf_by_position(node, pos):
    """
    Recursively searches for a leaf node with the given position in the syntax tree.

    Args:
        node (Node): The current node to search in.
        pos (int): The target position number to find.

    Returns:
        Leaf or None: The leaf node with the specified position, or None if not found.
    """
    if isinstance(node, Leaf):
        if node.position == pos:
            return node
    elif isinstance(node, UnaryNode):
        return find_leaf_by_position(node.child, pos)
    elif isinstance(node, BinaryNode):
        left_result = find_leaf_by_position(node.left, pos)
        if left_result:
            return left_result
        return find_leaf_by_position(node.right, pos)
    return None