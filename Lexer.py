import string
from Value import *
from TokenType import Token, TokenType


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.previous_char = None
        self.line_number = 0
        self.anchor_val = 0

    def error(self):
        raise Exception("Invalid character. Line number: " + str(self.line_number))
        
    def anchor(self):
        self.anchor_val = self.pos
        
    def rewind(self):
        """ Rewind to last set anchor """
        self.pos = self.anchor_val
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        if (self.pos > len(self.text) - 1):
            self.previous_char = self.current_char
            self.current_char = '\0'
        else:
            self.previous_char = self.current_char
            self.current_char = self.text[self.pos]

    def peek(self, num=1):
        if (self.pos + num < len(self.text)):
            return self.text[self.pos + num]
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
        """ Double quoted string """
        
        result = ""
        while (self.current_char != '\0'):
            if (self.current_char == '"'):
                break  # end of string
            elif (self.current_char == '\\' and self.peek() == '"'):
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
        return Token(TokenType.INTERP_STR, Value(result))

    def parse_literal_string(self):
        """ Single quoted string - no interpolation """
        
        result = ""
        while (self.current_char != '\0'):
            if (self.current_char == "'"):
                break  # end of string
            result += self.current_char
            self.advance()

        self.advance()
        return Token(TokenType.STR, Value(result))


    def get_id(self):
        name = ""
        while (
            self.current_char != '\0' and (self.current_char.isalnum() or self.current_char == '_')):
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
        elif (name == 'sub'):
            return Token(TokenType.FUNCTION_DECLARE, Value('sub'))
        elif (name == "do"):
            return Token(TokenType.DO, Value('do'))
        elif (name == "last"):
            return Token(TokenType.LAST, Value('last'))
        elif (name == "continue"):
            return Token(TokenType.CONTINUE, Value('continue'))
        elif (name == "until"):
            return Token(TokenType.UNTIL, Value('until'))
        else:
            return Token(TokenType.ID, Value(name))
            
    def parse_match_spec(self):
        match_regex = ''
        opts = ''
        start_char = self.current_char
        self.advance()
        last_char = None
        while self.current_char != start_char and last_char != '\\':
            last_char = self.current_char
            #if self.current_char == '\\' and last_char != '\\':
            match_regex += self.current_char
            self.advance()
        print match_regex
        self.advance()
        while self.current_char.isalpha():
            opts += self.current_char
            self.advance()
            
        return Token(TokenType.MATCH_SPEC, Value({'type': 'm', 'spec': match_regex, 'opts': opts}))
        
    def parse_trans_spec(self):
        search_spec = ''
        repl_spec = ''
        start_char = self.current_char
        self.advance()
        last_char = None
        while self.current_char != start_char and last_char != '\\':
            last_char = self.current_char
            search_spec += self.current_char
            self.advance()
            
        self.advance()
        last_char = None
        while self.current_char != start_char and last_char != '\\':
            last_char = self.current_char
            repl_spec += self.current_char
            self.advance()
            
        self.advance()
        return Token(TokenType.TRANS_SPEC, Value({'type': 'y', 'spec': search_spec, 'repl': repl_spec}))
        
    def parse_subs_spec(self):
        search_spec = ''
        repl_spec = ''
        opts = ''
        start_char = self.current_char
        self.advance()
        last_char = None
        while self.current_char != start_char and last_char != '\\':
            last_char = self.current_char
            search_spec += self.current_char
            self.advance()
            
        self.advance()
        last_char = None
        while self.current_char != start_char and last_char != '\\':
            last_char = self.current_char
            repl_spec += self.current_char
            self.advance()
            
        self.advance()
        while self.current_char.isalpha():
            opts += self.current_char
            self.advance()
            
        return Token(TokenType.SUBS_SPEC, Value({'type': 's', 'spec': search_spec, 'repl': repl_spec, 'opts': opts}))


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
                self.advance()
                return self.comment()

            if (self.current_char.isdigit()):
                if self.pos > 0:
                    # look back to see if prevous char was sigil
                    # so we don't muck up $1, $2, ... as id's
                    if self.peek(-1) not in [ '$', '@', '%' ]:
                        return self.parse_number()
                else:                
                    return self.parse_number()

            if (self.current_char == '"'):
                self.advance()
                return self.parse_string()

            if (self.current_char == "'"):
                self.advance()
                return self.parse_literal_string()
                
            if (self.current_char == 'm' and not self.peek().isalpha()):
                self.advance()
                return self.parse_match_spec()
                
            if ((self.current_char == 'y'  and not self.peek().isalpha()) 
                    or (self.current_char == 't' and self.peek() == 'r') and not self.peek(2).isalpha()):
                if (self.current_char == 'y'):
                    self.advance()
                    return self.parse_trans_spec()
                else:
                    self.advance()
                    self.advance()
                    return self.parse_trans_spec()
                    
            if (self.current_char == 's' and not self.peek().isalpha()):
                self.advance()
                return self.parse_subs_spec()

            if (self.current_char.isalnum() or self.current_char == '_'):
                if (self.current_char == 'e' and
                        self.peek() == 'q' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_EQ, Value('eq'))
                elif (self.current_char == 'n' and
                      self.peek() == 'e' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    if self.current_char.isspace():
                        return Token(TokenType.STR_NEQ, Value('ne'))
                    elif self.current_char == 'x' and self.peek() == 't':
                        self.advance()
                        self.advance()
                        return Token(TokenType.NEXT, Value('next'))
                elif (self.current_char == 'l' and
                      self.peek() == 't' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_LT, Value('lt'))
                elif (self.current_char == 'l' and
                      self.peek() == 'e' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_LE, Value('le'))
                elif (self.current_char == 'g' and
                      self.peek() == 'e' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_GE, Value('ge'))
                elif (self.current_char == 'g' and
                      self.peek() == 't' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return Token(TokenType.STR_GT, Value('gt'))
                else:
                    return self.get_id()
            
            if (self.current_char == '$' and self.peek() == ' '):
                self.advance()
                self.advance()
                return
            
            if (self.current_char == '$' and (self.peek().isalnum() or self.peek() == '_' or self.peek() == '#')):
                self.advance()
                if (self.current_char == '#'):
                    self.advance()
                    return Token(TokenType.LIST_MAX_INDEX, Value('$#'))
                else:
                    return Token(TokenType.SCALAR, Value('SCALAR'))

            if (self.current_char == '@' and (self.peek().isalnum() or self.peek() == '_')):
                self.advance()
                return Token(TokenType.LIST, Value('LIST'))
                
            if (self.current_char == '%' and (self.peek().isalnum() or self.peek() == '_')):
                self.advance()
                return Token(TokenType.HASH, Value('HASH'))
                
            if (self.current_char == '&'):
                if (self.peek() == '&'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.LOGAND, Value('&&'))
                self.advance()
                return Token(TokenType.AND, Value('&'))
                
            if (self.current_char == '!'):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return Token(TokenType.NEQ, Value('!='))
                elif (self.current_char == '~'):
                    self.advance()
                    return Token(TokenType.NOT_MATCH, Value('!~'))
                return Token(TokenType.NOT, Value('!'))
                
            if (self.current_char == '|'):
                if (self.peek() == '|'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.LOGOR, Value('||'))
                self.advance()
                return Token(TokenType.OR, Value('|'))

            if (self.current_char == '.'):
                self.advance()
                return Token(TokenType.STR_CONCAT, Value('.'))

            if (self.current_char == '='):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return Token(TokenType.EQ, Value('=='))
                elif (self.current_char == '~'):
                    self.advance()
                    return Token(TokenType.MATCH, Value('=~'))
                else:
                    return Token(TokenType.ASSIGN, Value('='))

            if (self.current_char == ','):
                self.advance()
                return Token(TokenType.COMMA, Value(','))

            if (self.current_char == '%'):
                self.advance()
                return Token(TokenType.MOD, Value('%'))

            if (self.current_char == ':'):
                if (self.peek() == ':'):
                    self.advance()
                    self.advance()
                    return Token(TokenType.COLONCOLON, Value('::'))
                self.advance()
                return Token(TokenType.COLON, Value(':'))
                
            if (self.current_char == '/'):
                return self.parse_match_spec()

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
                if (self.current_char == '+'):
                    self.advance()
                    return Token(TokenType.PLUSPLUS, Value('++'))
                if (self.current_char == '='):
                    self.advance()
                    return Token(TokenType.INCR, Value("+="))
                return Token(TokenType.PLUS, Value('+'))

            if (self.current_char == '-'):
                self.advance()
                if (self.current_char == '-'):
                    self.advance()
                    return Token(TokenType.MINUSMINUS, Value('--'))
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
            print self.current_char
            self.error()

        return Token(TokenType.EOF, Value("EOF"))
