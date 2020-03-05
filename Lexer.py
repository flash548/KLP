import string
from Value import *
from TokenType import Token, TokenType


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.line_number = 0

    def error(self):
        raise Exception("Invalid character. Line number: " +
                        str(self.line_number))

    def advance(self):
        self.pos += 1
        if (self.pos > len(self.text) - 1):
            self.current_char = '\0'
        else:
            self.current_char = self.text[self.pos]

    def peek(self):
        if (self.pos + 1 < len(self.text)):
            return self.text[self.pos + 1]
        else:
            return '\0'

    def skip_whitespace(self):
        while self.current_char != '\0' and self.current_char.isspace():
            self.advance()

    def comment(self):
        while self.current_char != '\0' and self.current_char != '\n':
            self.advance()

        return Token(TokenType.COMMENT, Value("COMMENT"))

    def parse_number(self):
        result = ""
        while self.current_char != '\0' and self.current_char.isdigit():
            result += self.current_char
            self.advance()

        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while self.current_char != '\0' and self.current_char.isdigit():
                result += self.current_char
                self.advance()
        else:
            return Token(TokenType.INTEGER, Value(int(result)))

        return Token(TokenType.FLOAT, Value(float(result)))

    def parse_hex(self):
        result = ""
        while (self.current_char != '\0' and (
                self.current_char in string.hexdigits)):
            result += self.current_char
            self.advance()

        return Token(TokenType.INTEGER, Value(int(result, 16)))

    def parse_string(self):
        result = ""
        while (self.current_char != '\0'):
            if (self.current_char == '"' and self.peek() != '"'):
                break  # end of string
            elif (self.current_char == '"' and self.peek() == '"'):
                self.advance()  # deal with double quote lierals
            elif (self.current_char == '\\' and self.peek() == 'n'):
                result += '\n'
                self.advance()
                self.advance()
                continue
            elif (self.current_char == '\\' and self.peek() == 'r'):
                result += '\r'
                self.advance()
                self.advance()
                continue
            elif (self.current_char == '\\' and self.peek() == 't'):
                result += '\t'
                self.advance()
                self.advance()
                continue
            result += self.current_char
            self.advance()

        self.advance()
        return Token(TokenType.STR, Value(result))

    def get_id(self):
        name = ""
        while (
            self.current_char != '\0' and (
                self.current_char.isalnum() or self.current_char == '_')):
            name += self.current_char
            self.advance()

        if (name == "if"):
            return Token(TokenType.IF, Value('if'))
        elif (name == "elsif"):
            return Token(TokenType.ELSIF, Value('elsif'))
        elif (name == "else"):
            return Token(TokenType.ELSE, Value('else'))
        elif (name == "while"):
            return Token(TokenType.WHILE, Value('while'))
        elif (name == "unless"):
            return Token(TokenType.UNLESS, Value('unless'))
        elif (name == "for"):
            return Token(TokenType.FOR, Value('for'))
        elif (name == "next"):
            return Token(TokenType.NEXT, Value('next'))
        elif (name == "last"):
            return Token(TokenType.LAST, Value('last'))
        elif (name == "continue"):
            return Token(TokenType.CONTINUE, Value('continue'))
        elif (name == "until"):
            return Token(TokenType.UNTIL, Value('until'))
        return Token(TokenType.ID, Value(name))

    def get_next_token(self):
        while (self.current_char != '\0'):
            if (self.current_char.isspace()):
                if (self.current_char == '\r' or self.current_char == '\n'):
                    if (self.current_char == '\r' and self.peek() == '\n'):
                        self.advance()
                    self.advance()
                    self.line_number += 1
                self.skip_whitespace()
                continue

            if (self.current_char == '0' and self.peek() == 'x'):
                self.advance()
                self.advance()
                return parse_hex()

            if (self.current_char == '0' and self.peek() == 'b'):
                self.advance()
                self.advance()
                return parse_binary()

            if (self.current_char == '#'):
                return self.comment()

            if (self.current_char.isdigit()):
                return self.parse_number()

            if (self.current_char == '"'):
                self.advance()
                return self.parse_string()

            if (self.current_char.isalnum()):
                if (self.current_char == 'e' and
                        self.peek() == 'q'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_EQ, Value('eq'))
                elif (self.current_char == 'n' and
                      self.peek() == 'e'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_NEQ, Value('ne'))
                elif (self.current_char == 'l' and
                      self.peek() == 't'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_LT, Value('lt'))
                elif (self.current_char == 'l' and
                      self.peek() == 'e'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_LE, Value('le'))
                elif (self.current_char == 'g' and
                      self.peek() == 'e'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_GE, Value('ge'))
                elif (self.current_char == 'g' and
                      self.peek() == 't'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_GT, Value('gt'))
                else:
                    return self.get_id()

            if (self.current_char == '$' and self.peek().isalnum()):
                self.advance()
                return Token(TokenType.CONTEXT, Value('SCALAR'))

            if (self.current_char == '@' and self.peek().isalnum()):
                self.advance()
                return Token(TokenType.CONTEXT, Value('LIST'))

            if (self.current_char == '.'):
                self.advance()
                return Token(TokenType.STR_CONCAT, Value('.'))

            if (self.current_char == '='):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return Token(TokenType.EQ, Value('=='))
                else:
                    return Token(TokenType.ASSIGN, Value('='))

            if (self.current_char == ','):
                self.advance()
                return Token(TokenType.COMMA, Value(','))

            if (self.current_char == '%'):
                self.advance()
                return Token(TokenType.MOD, Value('%'))

            if (self.current_char == ':'):
                self.advance()
                return Token(TokenType.COLON, Value(':'))

            if (self.current_char == ';'):
                self.advance()
                return Token(TokenType.SEMICOLON, Value(';'))

            if (self.current_char == '<'):
                if (self.peek() == '='):
                    self.advance()
                    self.advance()
                    return Token(TokenType.LTE, Value("<="))
                elif (self.peek() == '<'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.LSHIFT, Value("<<"))
                self.advance()
                return Token(TokenType.LT, Value("<"))

            if (self.current_char == '>'):
                if (self.peek() == '='):
                    self.advance()
                    self.advance()
                    return Token(TokenType.GTE, Value(">="))
                elif (self.peek() == '>'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.RSHIFT, Value(">>"))
                self.advance()
                return Token(TokenType.GT, Value(">"))

            if (self.current_char == '+'):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return Token(TokenType.INCR, Value("+="))
                return Token(TokenType.PLUS, Value('+'))

            if (self.current_char == '-'):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return Token(TokenType.DECR, Value("-="))
                return Token(TokenType.MINUS, Value("-"))

            if (self.current_char == '^'):
                self.advance()
                return Token(TokenType.XOR, Value('^'))

            if (self.current_char == "*"):
                self.advance()
                if (self.current_char == '*'):
                    self.advance()
                    return Token(TokenType.POW, Value('**'))
                else:
                    return Token(TokenType.MUL, Value('*'))

            if (self.current_char == '/'):
                self.advance()
                return Token(TokenType.DIV, Value('/'))

            if (self.current_char == '('):
                self.advance()
                return Token(TokenType.LPAREN, Value('('))

            if (self.current_char == ')'):
                self.advance()
                return Token(TokenType.RPAREN, Value(')'))

            if (self.current_char == '{'):
                self.advance()
                return Token(TokenType.LCURLY, Value('{'))

            if (self.current_char == '}'):
                self.advance()
                return Token(TokenType.RCURLY, Value('}'))

            if (self.current_char == '['):
                self.advance()
                return Token(TokenType.LBRACKET, Value('['))

            if (self.current_char == ']'):
                self.advance()
                return Token(TokenType.RBRACKET, Value(']'))

            self.error()

        return Token(TokenType.EOF, Value("EOF"))