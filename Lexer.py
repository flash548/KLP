import string
from Value import *
from TokenType import Token, TokenType


class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.previous_char = None
        self.prev_token = Token(TokenType.EOF, None)
        self.prev_scalar = False
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
        
    def make_token(self, tok_type, tok_val):
        t = Token(tok_type, tok_val)
        self.prev_token = t
        return t

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
            if (self.pos + num < 0): 
                return self.text[0]
            return self.text[self.pos + num]
        else:
            return '\0'

    def skip_whitespace(self):
        while self.current_char != '\0' and self.current_char.isspace():
            if self.current_char == '\r' and self.peek() == '\n':
                self.advance()
                self.advance()
                self.line_number += 1
                continue
            elif self.current_char == '\n':
                self.line_number += 1
                self.advance()
                continue
                
            self.advance()

    def comment(self):
        while self.current_char != '\0' and self.current_char != '\n':
            self.advance()
        return self.make_token(TokenType.COMMENT, Value("COMMENT"))

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
            return self.make_token(TokenType.INTEGER, Value(int(result)))

        return self.make_token(TokenType.FLOAT, Value(float(result)))

    def parse_hex(self):
        result = ""
        while (self.current_char != '\0' and (
                self.current_char in string.hexdigits)):
            result += self.current_char
            self.advance()

        return self.make_token(TokenType.INTEGER, Value(int(result, 16)))
        
    def parse_octal(self):
        result = ""
        while (self.current_char != '\0' and self.current_char.isdigit()):
            result += self.current_char
            self.advance()
            
        return self.make_token(TokenType.INTEGER, Value(int(result, 8)))

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
            elif (self.current_char == '\\' and self.peek() == '\\'):
                result += '\\'
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
        return self.make_token(TokenType.INTERP_STR, Value(result))

    def parse_literal_string(self):
        """ Single quoted string - no interpolation """
        
        result = ""
        while (self.current_char != '\0'):
            if (self.current_char == "'"):
                break  # end of string
            elif (self.current_char == '\\' and self.peek() == '\\'):
                result += '\\'
                self.advance()
                self.advance()
                continue
            result += self.current_char
            self.advance()

        self.advance()
        return self.make_token(TokenType.STR, Value(result))


    def get_id(self):
        name = ""
        first_char = True
        while (
            self.current_char != '\0' and (self.current_char.isalnum() or self.current_char == '_'
                or (self.current_char in ['_', '@', '#', '!', '^', '%', '\\', '/', '*', ',' ] 
                    and self.prev_token.type == TokenType.SCALAR and first_char))):
            name += self.current_char
            first_char = False
            self.advance()

        # check to see if its a label first
        if self.current_char == ':':
            self.advance()
            return self.make_token(TokenType.LABEL, Value(name))
            
        if (name == "if"):
            return self.make_token(TokenType.IF, Value('if'))
        elif (name == "elsif"):
            return self.make_token(TokenType.ELSIF, Value('elsif'))
        elif (name == "else"):
            return self.make_token(TokenType.ELSE, Value('else'))
        elif (name == "while"):
            return self.make_token(TokenType.WHILE, Value('while'))
        elif (name == "unless"):
            return self.make_token(TokenType.UNLESS, Value('unless'))
        elif (name == "for"):
            return self.make_token(TokenType.FOR, Value('for'))
        elif (name == 'sub'):
            return self.make_token(TokenType.FUNCTION_DECLARE, Value('sub'))
        elif (name == "do"):
            return self.make_token(TokenType.DO, Value('do'))
        elif (name == "last"):
            return self.make_token(TokenType.LAST, Value('last'))
        elif (name == "next"):
            return self.make_token(TokenType.NEXT, Value('next'))
        elif (name == "redo"):
            return self.make_token(TokenType.REDO, Value('redo'))
        elif (name == "goto"):
            return self.make_token(TokenType.GOTO, Value('goto'))
        elif (name == "continue"):
            return self.make_token(TokenType.CONTINUE, Value('continue'))
        elif (name == "until"):
            return self.make_token(TokenType.UNTIL, Value('until'))
        else:
            return self.make_token(TokenType.ID, Value(name))
            
    def parse_match_spec(self, with_m=False):
        start_pos = self.pos
        match_regex = ''
        opts = ''
        start_char = '/'
        if not with_m:
            start_char = self.current_char
        char_count = 1  # have to have 2 start char's for a good pat
        self.advance()
        last_char = None
        while (self.current_char != start_char) and self.current_char != '\0':
            last_char = self.current_char
            #if self.current_char == '\\' and last_char != '\\':
            match_regex += self.current_char
            self.advance()
        if self.current_char == start_char:
            char_count += 1
        self.advance()
        while self.current_char.isalpha():
            opts += self.current_char
            self.advance()
        
        if char_count == 2:
            return self.make_token(TokenType.MATCH_SPEC, Value({'type': 'm', 'spec': match_regex, 'opts': opts}))
        else:
            self.pos = start_pos # go back to the divide sign because its a math op, not a pattern
            return None
        
    def parse_trans_spec(self):
        search_spec = ''
        repl_spec = ''
        start_char = self.current_char
        self.advance()
        last_char = None
        while (self.current_char != start_char) and self.current_char != '\0':
            last_char = self.current_char
            search_spec += self.current_char
            self.advance()
            
        self.advance()
        last_char = None
        while (self.current_char != start_char) and self.current_char != '\0':
            last_char = self.current_char
            repl_spec += self.current_char
            self.advance()
            
        self.advance()
        return self.make_token(TokenType.TRANS_SPEC, Value({'type': 'y', 'spec': search_spec, 'repl': repl_spec}))
        
    def parse_subs_spec(self):
        search_spec = ''
        repl_spec = ''
        opts = ''
        start_char = self.current_char # establish the start char
        self.advance()
        last_char = None
        while (self.current_char != start_char) and self.current_char != '\0':
            last_char = self.current_char
            search_spec += self.current_char
            self.advance()
            
        self.advance()
        last_char = None
        while (self.current_char != start_char) and self.current_char != '\0':
            last_char = self.current_char
            repl_spec += self.current_char
            self.advance()
            
        self.advance()
        while self.current_char.isalpha():
            opts += self.current_char
            self.advance()
            
        return self.make_token(TokenType.SUBS_SPEC, Value({'type': 's', 'spec': search_spec, 'repl': repl_spec, 'opts': opts}))

    def parse_backticks(self):  
        cmdstr = ''
        while (self.current_char != '\0' and self.current_char != '`'):
            cmdstr += self.current_char
            self.advance()
        
        self.advance()        
        return self.make_token(TokenType.BACKTICKS, Value(cmdstr))

    def get_next_token(self):
        while (self.current_char != '\0'):
            # TODO: fix this mess, does a lookbehind to see if previous 
            # chars where '$' or '$#' or '@' so that we know we are to parse
            # an ID, and not some other token, say REPEAT, or NOT, etc...
            
            # first check if last char was SIGIL '$' or '$#'
            if ((self.pos != 0 and self.peek(-1) == '$') 
                or (self.pos != 0 and self.peek(-1) == '#' and self.peek(-2) == '$')
                or (self.pos != 0 and self.peek(-1) == '@')):
                if self.current_char == ' ':
                    self.advance()
                    return self.make_token(TokenType.ID, Value(' '))
                
                # TODO: fix this whole mess, because the Parser will do lookaheads
                # and rewinds, this destroys the whole concept of an accurate true 'previous token'
                # hack alert - manually set the prev token type to SCALAR since previous char was '$'
                if (self.current_char.isalnum() 
                        or (self.current_char in ['_', '@', '#', '!', '^', '%', '\\', '/', '*', ',' ])):
                    self.prev_token = Token(TokenType.SCALAR, Value('$'))
                    return self.get_id()
        
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
                return self.parse_hex()

            if (self.current_char == '0' and self.peek() == 'b'):
                self.advance()
                self.advance()
                return self.parse_binary()
                
            if (self.current_char == '#'):
                self.advance()
                return self.comment()
                
            # if (self.current_char == 'x'):
                # self.advance()
                # if (self.current_char == '='):
                    # self.advance()
                    # return self.make_token(TokenType.REPEAT_INCR, Value('x='))
                # return self.make_token(TokenType.REPEAT, Value('x'))
                
            if (self.current_char == 'x' and self.peek() == '='):
                self.advance()
                self.advance()
                return self.make_token(TokenType.REPEAT_INCR, Value('x='))
                
            if (self.current_char.isdigit()):
                if self.pos > 0:
                    # look back to see if prevous char was sigil
                    # so we don't muck up $1, $2, ... as id's
                    if self.peek(-1) not in [ '$', '@', '%' ]:
                        if (self.current_char == '0'):
                            return self.parse_octal()
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
                return self.parse_match_spec(True)
                
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
                if (self.current_char.upper() == 'E' and
                        self.peek().upper() == 'Q' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.STR_EQ, Value('eq'))
                elif (self.current_char == 'n' and
                      self.peek() == 'e' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.STR_NEQ, Value('ne'))
                elif (self.current_char == 'l' and
                      self.peek() == 't' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.STR_LT, Value('lt'))
                elif (self.current_char == 'l' and
                      self.peek() == 'e' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.STR_LE, Value('le'))
                elif (self.current_char == 'g' and
                      self.peek() == 'e' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.STR_GE, Value('ge'))
                elif (self.current_char == 'g' and
                      self.peek() == 't' and self.peek(2).isspace()):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.STR_GT, Value('gt'))
                else:
                    return self.get_id()
            
            if (self.current_char == '?'):
                self.advance()
                return self.make_token(TokenType.TERNARY, Value('TERNARY'))
            
            if (self.current_char == '$' and self.peek() == ' '):
                self.advance()
                self.prev_scalar = True
                return self.make_token(TokenType.SCALAR, Value('SCALAR'))
            
            if (self.current_char == '$' and (self.peek() == '#') and (self.peek(2).isalpha() or self.peek(2) == '_')):
                self.advance()
                self.advance()
                return self.make_token(TokenType.LIST_MAX_INDEX, Value('$#'))
            
            if (self.current_char == '$'):
                self.prev_scalar = True
                self.advance()
                return self.make_token(TokenType.SCALAR, Value('SCALAR'))

            if (self.current_char == '@' and (self.peek().isalnum() or self.peek() == '_')):
                self.advance()
                return self.make_token(TokenType.LIST, Value('LIST'))
                
            if (self.current_char == '%' and (self.peek().isalnum() or self.peek() == '_')):
                self.advance()
                return self.make_token(TokenType.HASH, Value('HASH'))
                
            if (self.current_char == '&'):
                if (self.peek() == '&'):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.LOGAND, Value('&&'))
                self.advance()
                return self.make_token(TokenType.AND, Value('&'))
                
            if (self.current_char == '!'):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return self.make_token(TokenType.NEQ, Value('!='))
                elif (self.current_char == '~'):
                    self.advance()
                    return self.make_token(TokenType.NOT_MATCH, Value('!~'))
                return self.make_token(TokenType.NOT, Value('!'))
                
            if (self.current_char == '|'):
                if (self.peek() == '|'):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.LOGOR, Value('||'))
                self.advance()
                return self.make_token(TokenType.OR, Value('|'))

            if (self.current_char == '.'):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return self.make_token(TokenType.STR_INCR, Value('.='))
                return self.make_token(TokenType.STR_CONCAT, Value('.'))

            if (self.current_char == '='):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return self.make_token(TokenType.EQ, Value('=='))
                elif (self.current_char == '~'):
                    self.advance()
                    return self.make_token(TokenType.MATCH, Value('=~'))
                else:
                    return self.make_token(TokenType.ASSIGN, Value('='))

            if (self.current_char == ','):
                self.advance()
                return self.make_token(TokenType.COMMA, Value(','))

            if (self.current_char == '%'):
                self.advance()
                return self.make_token(TokenType.MOD, Value('%'))

            if (self.current_char == ':'):
                if (self.peek() == ':'):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.COLONCOLON, Value('::'))
                self.advance()
                return self.make_token(TokenType.COLON, Value(':'))
                
            if (self.current_char == '/'):
                ret = self.parse_match_spec(False)
                if ret == None:
                    self.advance()
                    if (self.current_char == '='):
                        self.advance()
                        return self.make_token(TokenType.DIV_INCR, Value("/="))
                    return self.make_token(TokenType.DIV, Value('/'))
                else:
                    return ret

            if (self.current_char == ';'):
                self.advance()
                return self.make_token(TokenType.SEMICOLON, Value(';'))
                
            if (self.current_char == '`'):
                self.advance()
                return self.parse_backticks()

            if (self.current_char == '<'):
                if (self.peek() == '='):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.LTE, Value("<="))
                elif (self.peek() == '<'):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.LSHIFT, Value("<<"))
                elif (self.peek().isalpha()):
                    # check for spaceship
                    i = 1
                    bareword=''
                    while (self.peek(i).isalpha()):
                        bareword += self.peek(i)
                        i += 1
                    if self.peek(i) == '>':
                        for j in range(i+1):
                            self.advance()
                        return self.make_token(TokenType.SPACESHIP, Value(bareword))
                self.advance()
                return self.make_token(TokenType.LT, Value("<"))

            if (self.current_char == '>'):
                if (self.peek() == '='):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.GTE, Value(">="))
                elif (self.peek() == '>'):
                    self.advance()
                    self.advance()
                    return self.make_token(TokenType.RSHIFT, Value(">>"))
                self.advance()
                return self.make_token(TokenType.GT, Value(">"))

            if (self.current_char == '+'):
                self.advance()
                if (self.current_char == '+'):
                    self.advance()
                    return self.make_token(TokenType.PLUSPLUS, Value('++'))
                if (self.current_char == '='):
                    self.advance()
                    return self.make_token(TokenType.INCR, Value("+="))
                return self.make_token(TokenType.PLUS, Value('+'))

            if (self.current_char == '-'):
                self.advance()
                if (self.current_char == '-'):
                    self.advance()
                    return self.make_token(TokenType.MINUSMINUS, Value('--'))
                if (self.current_char == '='):
                    self.advance()
                    return self.make_token(TokenType.DECR, Value("-="))
                return self.make_token(TokenType.MINUS, Value("-"))

            if (self.current_char == '^'):
                self.advance()
                if (self.current_char == '='):
                    self.advance()
                    return self.make_token(TokenType.XOR_INCR, Value("^="))
                return self.make_token(TokenType.XOR, Value('^'))

            if (self.current_char == "*"):
                self.advance()
                if (self.current_char == '*'):
                    self.advance()
                    return self.make_token(TokenType.POW, Value('**'))
                elif (self.current_char == '='):
                    self.advance()
                    return self.make_token(TokenType.MUL_INCR, Value("*="))
                else:
                    return self.make_token(TokenType.MUL, Value('*'))
                    
            if (self.current_char == '('):
                self.advance()
                return self.make_token(TokenType.LPAREN, Value('('))

            if (self.current_char == ')'):
                self.advance()
                return self.make_token(TokenType.RPAREN, Value(')'))

            if (self.current_char == '{'):
                self.advance()
                return self.make_token(TokenType.LCURLY, Value('{'))

            if (self.current_char == '}'):
                self.advance()
                return self.make_token(TokenType.RCURLY, Value('}'))

            if (self.current_char == '['):
                self.advance()
                return self.make_token(TokenType.LBRACKET, Value('['))

            if (self.current_char == ']'):
                self.advance()
                return self.make_token(TokenType.RBRACKET, Value(']'))
            print self.current_char
            self.error()

        return self.make_token(TokenType.EOF, Value("EOF"))
