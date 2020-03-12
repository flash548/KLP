from AST import *
from TokenType import *


class Parser:
    def __init__(self, lexer):
        self.lineNumber = 1
        self.lex = lexer
        self.current_token = self.lex.get_next_token()

    def error(self):
        raise Exception("Invalid syntax on line: " + str(self.lineNumber))

    def parse(self):
        return expr()

    def eat(self, tokType):
        if self.current_token.type == tokType:
            if tokType == TokenType.NEWLINE:
                self.lineNumber += 1
            self.current_token = self.lex.get_next_token()
        else:
            print tokType, self.current_token.type
            self.error()

    def eat_end_of_statement(self):
        if self.current_token.type == TokenType.SEMICOLON:
            self.eat(TokenType.SEMICOLON)
    
    # program <- statement_list EOF
    def program(self):
        return RootNode(self.statement_list())

    # statement_list <- statement+
    def statement_list(self):
        nodes = []
        node = self.statement()
        nodes.append(node)

        while self.current_token.type != TokenType.EOF:
            self.eat_end_of_statement()
            
            # incase this statement was last in the file... check agian
            if (self.current_token.type == TokenType.EOF): break
            nodes.append(self.statement())

        if self.current_token.type == TokenType.ID:
            self.error()

        return nodes

    # statement <- Comment / Func_Decl / Cond / Loop / Block / Sideff ';'
    def statement(self):
        if self.current_token.type == TokenType.COMMENT:
            return AST()
        elif self.current_token.type == TokenType.FUNCTION_DECLARE:
            return self.function_declare_statement()
        elif self.current_token.type == TokenType.IF: # TODO: unless
            return self.cond_statement()
        elif self.current_token.type == TokenType.WHILE: # TODO: continue
            return self.while_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.for_statement()
        elif self.current_token.type == TokenType.LCURLY:
            self.eat(TokenType.LCURLY)
            return self.statement_list()
            self.eat(TokenType.RCURLY)
        else: # TODO: if/unless 
            return self.expression()

        raise Exception("Invalid statement, line number: " +
                        str(self.lineNumber))            
    
    def if_statement(self):
        pass

    def while_statement(self):
        pass

    def function_declare_statement(self):
        pass

    def expression(self):
        result = self.term()
        while self.current_token.type in (
                TokenType.PLUS,
                TokenType.MINUS,
                TokenType.STR_CONCAT,
                TokenType.LSHIFT,
                TokenType.RSHIFT):

            token = self.current_token
            self.eat(self.current_token.type)
            result = BinOpNode(result, token.value, self.term())

        return result

    def term(self):
        result = self.factor()
        while self.current_token.type in (
                TokenType.MUL,
                TokenType.DIV,
                TokenType.POW,
                TokenType.AND,
                TokenType.OR,
                TokenType.XOR,
                TokenType.GT,
                TokenType.GTE,
                TokenType.LT,
                TokenType.LTE,
                TokenType.EQ,
                TokenType.NEQ,
                TokenType.STR_EQ,
                TokenType.STR_LT,
                TokenType.STR_LE,
                TokenType.STR_GT,
                TokenType.STR_GE,
                TokenType.MOD):

            token = self.current_token
            self.eat(self.current_token.type)
            result = BinOpNode(result, token.value, self.factor())

        return result

    def factor(self):
        token = self.current_token
        if (token.type == TokenType.SCALAR):
            self.eat(TokenType.SCALAR)
            name = str(self.current_token.value)
            self.eat(TokenType.ID)
            index_expr = None
            if (self.current_token.type == TokenType.LBRACKET):
                self.eat(TokenType.LBRACKET)
                index_expr = self.expression()
                self.eat(TokenType.RBRACKET)
            if (self.current_token.type == TokenType.ASSIGN):
                self.eat(TokenType.ASSIGN)
                if (self.current_token.type == TokenType.LPAREN):
                    return ScalarAssignNode(name, self.consume_list(), index_expr)
                else:
                    return ScalarAssignNode(name, self.expression(), index_expr)
            else:
                return ScalarVarNode(name, index_expr)
        elif (token.type == TokenType.LIST):
            self.eat(TokenType.LIST)
            name = str(self.current_token.value)
            self.eat(TokenType.ID)
            if (self.current_token.type == TokenType.ASSIGN):
                self.eat(TokenType.ASSIGN)                
                return ListAssignNode(name, self.consume_list())
            else:
                return ListVarNode(name)      
        elif (token.type == TokenType.LBRACKET):
            self.eat(TokenType.LBRACKET)
            anon_list = self.consume_list(TokenType.RBRACKET)
            return AnonListNode(anon_list)
        elif (token.type == TokenType.PLUS):
            self.eat(TokenType.PLUS)
            return UnOpNode(Value('+'), self.factor())
        elif (token.type == TokenType.MINUS):
            self.eat(TokenType.MINUS)
            return UnOpNode(Value('-'), self.factor())
        elif (token.type == TokenType.NOT):
            self.eat(TokenType.NOT)
            return UnOpNode(Value('!'), self.factor())
        elif (token.type == TokenType.ID):
            name = token.value
            self.eat(TokenType.ID)
            if (str(name) in TokenType.BUILTINS):
                # its a builtin
                args = self.consume_list()
                return BuiltInFunctionNode(name, args)
            else:
                # its a BAREWORD, croak for now
                print "CROAK!"
                return AST()
        elif (token.type == TokenType.STR):
            self.eat(TokenType.STR)
            return ValueNode(token.value)
        elif (token.type == TokenType.INTEGER):
            self.eat(TokenType.INTEGER)
            return ValueNode(token.value)
        elif (token.type == TokenType.FLOAT):
            self.eat(TokenType.FLOAT)
            return ValueNode(token.value)
        elif (token.type == TokenType.LPAREN):
            self.eat(TokenType.LPAREN)
            result = self.expression()
            self.eat(TokenType.RPAREN)
            return result

        raise Exception("Unknown token in factor(): " + str(token.value))
        
    def consume_list(self, ender=None):
        list_elems = []
        if ender == None:
            end_token = TokenType.SEMICOLON
            if (self.current_token.type == TokenType.LPAREN):
                end_token = TokenType.RPAREN
                self.eat(TokenType.LPAREN)
        else:
            end_token = ender
        while ((self.current_token.type != end_token) and
                (self.current_token.type != TokenType.SEMICOLON)):
            list_elems.append(self.expression())
            if (self.current_token.type == TokenType.COMMA):
                self.eat(TokenType.COMMA)
        self.eat(end_token)
        return list_elems
