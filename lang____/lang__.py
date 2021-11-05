# CONSTANTS
DIGITS = '0123456789'

## ERROR CLASS
class Error:
    def __init__(self,pos_start,pos_end, error_name, details):      # here we are giving the start and end position so that i can get exact index whenever error occurs
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details  = details
    def as_string(self):
        result = f'{self.error_name}: {self.details}'
        result += f'File{self.pos_start.fn}, line{self.pos_start.ln + 1}'
        return result
class IllegalCharError(Error):
    def __init__(self,pos_start, pos_end, details):
        super.__init__('IllegalChar',pos_start, pos_end, details)



## position class

class Position:
    def __init__(self, idx, ln, col, fn, ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn                    # file name
        self.ftxt = ftxt                # text in the file
    def advance(self,current_char):
        self.idx += 1
        self.col += 1
        if current_char == '\n':
            self.ln += 1
            self.col = 0
        return self
    def copy(self):
        return Position(self.idx,self.ln,self.col,self.fn, self.ftxt)

# __repr__ return printable object
# we are creating the tokens

TT_INT = 'TT_INT'
TT_FLOAT = 'FLOAT'
TT_PLUS = 'PLUS'
TT_MINUS = 'MINUS'
TT_MUL = 'MUL'
TT_DIV = 'DIV'
TT_LPAREN = 'LPAREN'            # LEFT PARENTHISIS
TT_RPAREN = 'RPAREN'

class Token:
    def __init__(self,type_, value = None):
        self.type = type_
        self.value = value
    def __repr__(self):
        if self.value:
            return f'{self.type}:{self.value}'
        return f'{self.type}'

## Lexer

class Lexer:
    def __init__(self, text, fn):
        self.fn = fn
        self.text = text
        self.pos = Position(-1,0,-1, fn, text)
        self.current_char = None         # we dont need to keep track of character in the constructor
        self.advance()
    def advance(self):
        self.pos.advance(self.current_char)
        if self.pos.idx < len(self.text):
            self.current_char = self.text[self.pos.idx]
        else:
            self.current_char = None

    def make_token(self):
        tokens = []
        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_numbers())          # here we are calling a method to make integers or float to add into tokens
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            else:
                # if dont get character we are looking for return an error
                pos_start = self.pos.copy()
                char = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start,self.pos,"'",char,"'")

        return tokens, None
    def make_numbers(self):
        num_str = ''
        dot_count = 0
        while self.current_char != None and self.current_char in DIGITS + '.':      # here we are checking whether there is a dot in the number or not if yes than the tokens will be of float type
            if self.current_char == '.':
                if dot_count == 1:
                    break
                dot_count += 1
                num_str += '.'
            else:
                num_str += self.current_char
            self.advance()
        if dot_count == 0:
            return Token(TT_INT , int(num_str))             # if there is no dot then we will add an integer in token class
        else:
            return Token(TT_FLOAT , float(num_str))

## NODES


class NumberNode:                           # here we are creating a syntax tree to check the opeartions
    def __init__(self, tok):
        self.tok = tok
    def __repr__(self):
        return  f'{self.tok}'
class BinOpNode:
    def __init__(self, left_node, op_tok, right_node):          # eg: 5+2*3 here the syntax tree of these are plus as the main root and 5 and * as the left and  right roots of plus
        self.left_node = left_node                              # as * as the root 2 and 3 as the left and right root respectively
        self.op_tok = op_tok
        self.rigth_node = right_node
    def __repr__(self):
        return f'({self.left_node}, {self.op_tok}, {self.rigth_node})'


## Parser

class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()
    def advance(self):
        self.tok_idx += 1
        if self.tok_idx < len(self.tokens):
            self.current_tok = self.tokens[self.tok_idx]
        return self.current_tok
    def parse(self):
        res = self.expr()
        return res
    def factor(self):                               # syntax tree consists of grammar mainly contains factors, term, expr
        tok = self.current_tok
        if tok.type in (TT_INT, TT_FLOAT):          # here we are checking whether our current token is a number or not
            self.advance()
            return NumberNode(tok)                  # if it is a number then return a node of a number tree

    def term(self):
        return self.bin_op(self.factor, (TT_MUL, TT_DIV))
    def expr(self):
        return self.bin_op(self.term, (TT_PLUS, TT_MINUS))
    def bin_op(self, func, ops):           # binery opeartion
        left = func()

        while self.current_tok.type in ops:
            op_tok = self.current_tok
            self.advance()
            right = func()
            left = BinOpNode(left, op_tok, right)

        return left

## RUN

def run(fn, text):
    lexer = Lexer(fn, text)
    tokens, error = lexer.make_token()
    if error:
        return None,error
    ## Generating Abstract syntax tree
    parser = Parser(tokens)
    ast = parser.parse()

    return ast, None

