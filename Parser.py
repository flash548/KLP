from AST import *
from TokenType import *


class Parser:
    def __init__(self, lexer):
        self.lineNumber = 1
        self.lex = lexer
        self.current_token = self.lex.get_next_token()
        self.statement_modifier_tokens = [ TokenType.IF, TokenType.UNLESS,
            TokenType.UNTIL, TokenType.WHILE ];

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
            print "Token Eat error: " + tokType, self.current_token.type
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
            self.eat(TokenType.COMMENT)
            return AST()
        elif self.current_token.type == TokenType.FUNCTION_DECLARE:
            return self.function_declare_statement()
        elif self.current_token.type in [TokenType.IF, TokenType.UNLESS]:
            return self.if_statement()
        elif self.current_token.type in [TokenType.WHILE, TokenType.UNTIL]:
            return self.while_statement()
        elif self.current_token.type == TokenType.FOR:
            return self.for_statement()
        elif self.current_token.type == TokenType.LCURLY:
            self.eat(TokenType.LCURLY)
            return self.statement_list()
            self.eat(TokenType.RCURLY)
        elif self.current_token.type == TokenType.LAST:
            self.eat(TokenType.LAST)
            return self.check_for_conditional(LastNode())
        elif self.current_token.type == TokenType.NEXT:
            self.eat(TokenType.NEXT)
            return self.check_for_conditional(NextNode())
        else:
            return self.check_for_conditional(self.expression())

        raise Exception("Invalid statement, line number: " +
                        str(self.lineNumber))                            
    
    def check_for_conditional(self, node):
        """ Checks for a statement modifier (if, unless, while, until)... """
        
        if (self.current_token.type == TokenType.IF):
            self.eat(TokenType.IF)
            expr = self.expression();
            return IfNode(expr, [ node ], [], [], [], False)
        elif (self.current_token.type == TokenType.UNLESS):
            self.eat(TokenType.UNLESS)
            expr = self.expression();
            return IfNode(expr, [ node ], [], [], [], True)
        elif (self.current_token.type == TokenType.WHILE):
            self.eat(TokenType.WHILE)
            expr = self.expression();
            return WhileNode(expr, [ node ], [], False)
        elif (self.current_token.type == TokenType.UNTIL):
            self.eat(TokenType.UNTIL)
            expr = self.expression();
            return WhileNode(expr, [ node ], [], True)
        else:
            return node
    
    def if_statement(self):
        if (self.current_token.type == TokenType.UNLESS):
            self.eat(TokenType.UNLESS)
            invert_logic = True
        else:
            self.eat(TokenType.IF)
            invert_logic = False
        expr = self.expression()
        self.eat(TokenType.LCURLY)
        if_clause = []
        else_if_conds = []
        else_if_clauses = []
        else_clause = []
        while (self.current_token.type != TokenType.RCURLY):
            if_clause.append(self.statement())
            self.eat_end_of_statement()
        self.eat(TokenType.RCURLY)
        
        if (self.current_token.type == TokenType.ELSIF):
            while (self.current_token.type == TokenType.ELSIF):
                self.eat(TokenType.ELSIF)
                else_if_conds.append(self.expression())
                self.eat(TokenType.LCURLY)
                clauses = []
                while (self.current_token.type != TokenType.RCURLY):
                    clauses.append(self.statement())
                    self.eat_end_of_statement()
                else_if_clauses.append(clauses)
                self.eat(TokenType.RCURLY)
        
        if (self.current_token.type == TokenType.ELSE):
            self.eat(TokenType.ELSE)
            self.eat(TokenType.LCURLY)
            while (self.current_token.type != TokenType.RCURLY):
                else_clause.append(self.statement())
                self.eat_end_of_statement()
            self.eat(TokenType.RCURLY)
        return IfNode(expr, if_clause, else_if_conds, else_if_clauses, else_clause, invert_logic)

    def for_statement(self):
        self.eat(TokenType.FOR)
        self.eat(TokenType.LPAREN)
        initial = self.expression()
        self.eat(TokenType.SEMICOLON)
        cond = self.expression()
        self.eat(TokenType.SEMICOLON)
        end = self.expression()
        self.eat(TokenType.RPAREN)
        self.eat(TokenType.LCURLY)
        body = []
        while (self.current_token.type != TokenType.RCURLY):
            body.append(self.statement())
            self.eat_end_of_statement()
        self.eat(TokenType.RCURLY)
        return ForNode(initial, cond, end, body)

    def while_statement(self):
        if (self.current_token.type == TokenType.UNTIL):
            self.eat(TokenType.UNTIL)
            invert_logic = True
        else:
            self.eat(TokenType.WHILE)
            invert_logic = False
        expr = self.expression()
        self.eat(TokenType.LCURLY)
        while_clause = []
        continue_clause = []
        while (self.current_token.type != TokenType.RCURLY):
            while_clause.append(self.statement())
            self.eat_end_of_statement()
        self.eat(TokenType.RCURLY)
        if (self.current_token.type == TokenType.CONTINUE):
            self.eat(TokenType.CONTINUE)
            self.eat(TokenType.LCURLY)
            while (self.current_token.type != TokenType.RCURLY):
                continue_clause.append(self.statement())
                self.eat_end_of_statement()
            self.eat(TokenType.RCURLY)
        return WhileNode(expr, while_clause, continue_clause, invert_logic)

    def function_declare_statement(self):
        self.eat(TokenType.FUNCTION_DECLARE)
        name = str(self.current_token.value)
        if (name not in AST.func_table):
            AST.func_table[name] = None
        
        self.eat(TokenType.ID)
        self.eat(TokenType.LCURLY)
        func_body = []
        while (self.current_token.type != TokenType.RCURLY):
            func_body.append(self.statement())
            self.eat_end_of_statement()
        self.eat(TokenType.RCURLY)
        root = RootNode(func_body)
        AST.func_table[name] = root
        return AST()
    
    def do_statement(self):
        self.eat(TokenType.LCURLY)
        do_body = []
        while (self.current_token.type != TokenType.RCURLY):
            do_body.append(self.statement())
            self.eat_end_of_statement()
        self.eat(TokenType.RCURLY)
        root = RootNode(do_body)
        expr = None
        # check for do-while
        if (self.current_token.type == TokenType.WHILE):
            self.eat(TokenType.WHILE)
            expr = self.expression()
            self.eat_end_of_statement()
            return DoWhileNode(do_body, expr)
        else:
            return DoStatementNode(do_body)
        
    def function_call(self):
        name = str(self.current_token.value)
        self.eat(TokenType.ID)
        args = self.consume_list()
        return FuncCallNode(name, args)

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
                TokenType.LOGAND,
                TokenType.LOGOR,
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
                TokenType.STR_NEQ,
                TokenType.STR_LT,
                TokenType.STR_LE,
                TokenType.STR_GT,
                TokenType.STR_GE,
                TokenType.MOD):

            token = self.current_token
            self.eat(self.current_token.type)
            if token.type in (TokenType.LOGAND, TokenType.LOGOR):
                result = LogicalOpNode(token.value, result, self.factor())
            else:
                result = BinOpNode(result, token.value, self.factor())

        return result

    def factor(self):
        token = self.current_token
        print str(token)
        
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
            elif (self.current_token.type == TokenType.INCR):
                self.eat(TokenType.INCR)
                return ScalarIncrDecrNode(name, self.expression(), '+=')
            elif (self.current_token.type == TokenType.DECR):
                self.eat(TokenType.DECR)
                return ScalarIncrDecrNode(name, self.expression(), '-=')
            elif (self.current_token.type == TokenType.PLUSPLUS):
                self.eat(TokenType.PLUSPLUS)
                return ScalarIncrDecrNode(name, None, 'post++')
            elif (self.current_token.type == TokenType.MINUSMINUS):
                self.eat(TokenType.MINUSMINUS)
                return ScalarIncrDecrNode(name, None, 'post--')
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
                
        elif (token.type == TokenType.LIST_MAX_INDEX):
            self.eat(TokenType.LIST_MAX_INDEX)
            name = ''
            if (self.current_token.type == TokenType.ID):
                name = str(self.current_token.value)
                self.eat(TokenType.ID)
            return ListMaxIndexNode(name)
                
        elif (token.type == TokenType.LBRACKET):
            self.eat(TokenType.LBRACKET)
            anon_list = self.consume_list(TokenType.RBRACKET)
            return AnonListNode(anon_list)
            
        elif (token.type == TokenType.DO):
            self.eat(TokenType.DO)
            if (self.current_token.type == TokenType.ID):
                # a sub call
                return self.function_call()
            else:
                # a DO block
                return self.do_statement()
                
        elif (token.type == TokenType.PLUS):
            self.eat(TokenType.PLUS)
            return UnOpNode(Value('+'), self.factor())
            
        elif (token.type == TokenType.MINUS):
            self.eat(TokenType.MINUS)
            return UnOpNode(Value('-'), self.factor())
            
        elif (token.type == TokenType.NOT):
            self.eat(TokenType.NOT)
            return UnOpNode(Value('!'), self.factor())
            
        elif (token.type == TokenType.PLUSPLUS):
            # prefix incr
            self.eat(TokenType.PLUSPLUS)
            # we can assume next token is ID for the variable name
            self.eat(TokenType.SCALAR)
            name = str(self.current_token.value)
            self.eat(TokenType.ID)
            return ScalarIncrDecrNode(name, None, '++')
            
        elif (token.type == TokenType.MINUSMINUS):
            # prefix decr
            self.eat(TokenType.MINUSMINUS)
            # we can assume next token is ID for the variable name
            self.eat(TokenType.SCALAR)
            name = str(self.current_token.value)
            self.eat(TokenType.ID)
            return ScalarIncrDecrNode(name, None, '--')
            
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
                
        elif (token.type == TokenType.INTERP_STR):
            self.eat(TokenType.INTERP_STR)
            return InterpolatedValueNode(token.value)
            
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
        """ This is kinda hacky... it attempts to read a list, whether for
            array purposes or for function arguments.  List can start with
            an LPAREN or not.  If not, then end of list is either an RPAREN,
            SEMICOLON or a statement modifier (if, until, unless, while...)
            
            If ender is a SEMICOLON, stop processig the list, but don't eat it
            since the statement() func will take care of eating end of statements
        """
        
        list_elems = []
        if ender == None:
            end_token = TokenType.SEMICOLON
            if (self.current_token.type == TokenType.LPAREN):
                end_token = TokenType.RPAREN
                self.eat(TokenType.LPAREN)
        else:
            end_token = ender
            
        while ((self.current_token.type != end_token) and
                (self.current_token.type != TokenType.SEMICOLON) and
                (self.current_token.type != TokenType.RPAREN) and
                (self.current_token.type not in self.statement_modifier_tokens)):
            list_elems.append(self.expression())
            if (self.current_token.type == TokenType.COMMA):
                self.eat(TokenType.COMMA)
        if (self.current_token.type not in self.statement_modifier_tokens):
            if (self.current_token.type == end_token and end_token != TokenType.SEMICOLON):
                self.eat(end_token)
        return list_elems
