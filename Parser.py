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
                        if tokType == TokenType.NEWLINE: self.lineNumber += 1
                        self.current_token = self.lex.get_next_token()
                else:
                        print tokType, self.current_token.type
                        self.error()
        
        def eat_end_of_statement(self):
                if self.current_token.type == TokenType.SEMICOLON:
                        self.eat(TokenType.SEMICOLON)
        
        def program(self):
                return RootNode(self.statement_list())
                
        def statement_list(self):
                nodes = []
                node = self.statement()
                nodes.append(node)
                
                while self.current_token.type != TokenType.EOF:
                        self.eat_end_of_statement()
                        nodes.append(self.statement())
                        
                if self.current_token.type == TokenType.ID:
                        self.error()
                        
                return nodes
                
        def statement(self):
                if self.current_token.type == TokenType.IF:
                        return self.if_statement()
                elif self.current_token.type == TokenType.WHILE:
                        return self.while_statement()
                elif self.current_token.type == TokenType.FUNCTION_DECLARE:
                        return self.function_declare_statement()
                else:
                        return self.expression()
                                                
                raise Exception("Invalid statement, line number: " + str(self.lineNumber))
        
        def if_statement(self):
            pass
            
        def while_statement(self):
            pass
            
        def function_declare_statement(self):
            pass
                
        def expression(self):
            result = self.term()
            print "Expr: Token type: " + str(self.current_token) 
            while self.current_token.type in (TokenType.PLUS, TokenType.MINUS, TokenType.STR_CONCAT,
                  TokenType.LSHIFT, TokenType.RSHIFT):
                
                token = self.current_token    
                self.eat(self.current_token.type)
                result = BinOpNode(result, token.value, self.term())
                
            return result
                
        def term(self):
            result = self.factor()
            print "Term: " + str(self.current_token) 
            while self.current_token.type in (TokenType.MUL, TokenType.DIV, TokenType.POW, 
                    TokenType.AND, TokenType.OR, TokenType.XOR, TokenType.GT, TokenType.GTE,
                    TokenType.LT, TokenType.LTE, TokenType.EQ, TokenType.NEQ, TokenType.STR_EQ,
                    TokenType.STR_LT, TokenType.STR_LE, TokenType.STR_GT, TokenType.STR_GE,
                    TokenType.MOD):
                
                token = self.current_token
                self.eat(self.current_token.type)
                result = BinOpNode(result, token.value, self.factor()) 
                
            return result
            
        def factor(self):
            token = self.current_token
            print "Factor: " + str(self.current_token)
            if (token.type == TokenType.PLUS):
                self.eat(TokenType.PLUS)
                return UnOpNode(Value('+'), self.factor())
            elif (token.type == TokenType.MINUS):
                self.eat(TokenType.MINUS)
                return UnOpNode(Value('-'), self.factor())
            elif (token.type == TokenType.NOT):
               self.eat(TokenType.NOT)
               return UnOpNode(Value('!'), self.factor())
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
