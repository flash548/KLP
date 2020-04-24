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
        elif self.current_token.type in [TokenType.SCALAR, TokenType.LIST, TokenType.LPAREN]:
            return self.assignment()
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
    
    def assignment(self):
    
        # look ahead to make sure this is an assignment statement
        self.lex.anchor() # insurance policy 
        isAssign = False
        found_lparen = False
        found_comma = False
        tok = self.lex.get_next_token()
        while (tok.type != TokenType.SEMICOLON):
            if (tok.type == TokenType.COMMA):
                found_comma = True
            if (tok.type == TokenType.COMMA):
                found_lparen = True
            if (tok.type == TokenType.ASSIGN):
                # this is an assign statement
                isAssign = True
                break
            tok = self.lex.get_next_token()
        
        self.lex.rewind()
        if not isAssign:
            # go back and treat the statement as expression
            return self.check_for_conditional(self.expression())
    
        # multiple assignments, in python parlance 'unpacking' an rvalue
        # in list context.  This is kinda hacky, but here we gotta discern
        # a mult assignment from a regular ole expression encased in parens
        # so we gotta look for an assignment op ahead of time
        if ((found_lparen or found_comma)):
            ender = TokenType.ASSIGN
            if (found_lparen): 
                self.eat(TokenType.LPAREN)
                ender = TokenType.RPAREN
            
            # build list of varnames we'll unpack to
            vars = []
            while (self.current_token.type != ender):
                if self.current_token.type == TokenType.SCALAR:
                    self.eat(TokenType.SCALAR)
                    vars.append('$' + str(self.current_token.value))
                    self.eat(TokenType.ID)
                elif self.current_token.type == TokenType.LIST:
                    self.eat(TokenType.LIST)
                    vars.append('@' + str(self.current_token.value))
                    self.eat(TokenType.ID)
                else:
                    print self.current_token.type
                    raise Exception("Error parsing unpack assignments")
                
                if self.current_token.type == TokenType.COMMA:
                    self.eat(TokenType.COMMA)
            
            if (ender == TokenType.RPAREN): self.eat(TokenType.RPAREN)
            self.eat(TokenType.ASSIGN)
            rval = self.consume_list()
            return UnpackAssignNode(vars, rval)
            
        
        # wasn't a multi assignment, treat as expresion
        return self.check_for_conditional(self.expression())
        
    def if_statement(self):
        if (self.current_token.type == TokenType.UNLESS):
            self.eat(TokenType.UNLESS)
            invert_logic = True
        else:
            self.eat(TokenType.IF)
            invert_logic = False
        #self.eat(TokenType.LPAREN)
        expr = self.statement()
        #self.eat(TokenType.RPAREN)
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
                self.eat(TokenType.LPAREN)
                else_if_conds.append(self.statement())
                self.eat(TokenType.RPAREN)
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
        initial = None
        if self.current_token.type != TokenType.SEMICOLON:
            initial = self.statement()
        self.eat(TokenType.SEMICOLON)
        cond = None
        if self.current_token.type != TokenType.SEMICOLON:
            cond = self.statement()
        self.eat(TokenType.SEMICOLON)
        end = None
        if self.current_token.type != TokenType.RPAREN:
            end = self.statement()
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
        self.eat(TokenType.LPAREN)
        expr = self.statement()
        self.eat(TokenType.RPAREN)
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
            expr = self.statement()
            #self.eat_end_of_statement()
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
                TokenType.LOGAND,
                TokenType.LOGOR,
                TokenType.LSHIFT,
                TokenType.RSHIFT):

            token = self.current_token
            self.eat(self.current_token.type)
            if token.type in (TokenType.LOGAND, TokenType.LOGOR):
                result = LogicalOpNode(token.value, result, self.term())
            else:
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
                TokenType.STR_NEQ,
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
            
        # '$' sigil -> but its tricky bc it could be assigning
        # to a list or hash or scalar!!
        if (token.type == TokenType.SCALAR):
            self.eat(TokenType.SCALAR)
            name = str(self.current_token.value)
            self.eat(TokenType.ID)
            index_expr = None
            if (self.current_token.type == TokenType.LBRACKET):
                # list index expr
                self.eat(TokenType.LBRACKET)
                index_expr = self.expression()
                self.eat(TokenType.RBRACKET)
                
            if (self.current_token.type == TokenType.LCURLY):
                # hash index expr
                self.eat(TokenType.LCURLY)
                index_expr = self.expression()
                self.eat(TokenType.RCURLY)
                
            if (self.current_token.type == TokenType.ASSIGN):
                self.eat(TokenType.ASSIGN)
                
                if (self.current_token.type == TokenType.LPAREN):
                    return ScalarAssignNode(name, self.consume_list(), index_expr)
                else:
                    return ScalarAssignNode(name, self.expression(), index_expr)
            
            elif (self.current_token.type == TokenType.MATCH):
                self.eat(TokenType.MATCH)
                if self.current_token.type == TokenType.MATCH_SPEC:
                    spec = self.current_token.value
                    self.eat(TokenType.MATCH_SPEC)
                    return MatchNode(name, index_expr, spec)
                elif (self.current_token.type == TokenType.TRANS_SPEC):
                    spec = self.current_token.value
                    self.eat(TokenType.TRANS_SPEC)
                    return TransNode(name, index_expr, spec)
                elif (self.current_token.type == TokenType.SUBS_SPEC):
                    spec = self.current_token.value
                    self.eat(TokenType.SUBS_SPEC)
                    return SubsNode(name, index_expr, spec)
                else:
                    raise Exception ("Parser Error in / / expression!")
            
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
        
        # handle a Match spec by itself - on the $_ var
        elif (token.type == TokenType.MATCH_SPEC):
            spec = self.current_token.value
            self.eat(TokenType.MATCH_SPEC)
            return MatchNode(None, None, spec)
        
        # handle a Transliteration spec by itself - on the $_ var        
        elif (token.type == TokenType.TRANS_SPEC):
            spec = self.current_token.value
            self.eat(TokenType.TRANS_SPEC)
            return TransNode(None, None, spec)
            
        # handle a Substitution spec by itself - on the $_ var        
        elif (token.type == TokenType.SUBS_SPEC):
            spec = self.current_token.value
            self.eat(TokenType.SUBS_SPEC)
            return SubsNode(None, None, spec)
        
        # '@' sigil -> interprets rvalue expr in list context
        elif (token.type == TokenType.LIST):
            self.eat(TokenType.LIST)
            name = str(self.current_token.value)
            self.eat(TokenType.ID)
            if (self.current_token.type == TokenType.ASSIGN):
                self.eat(TokenType.ASSIGN)                
                return ListAssignNode(name, self.consume_list())
            else:
                return ListVarNode(name)  

        # '%' sigil
        elif (token.type == TokenType.HASH):
            self.eat(TokenType.HASH)
            name = str(self.current_token.value)
            self.eat(TokenType.ID)
            return HashVarNode(name)
                
        # '$#" twigil
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
                return ValueNode(str(name))
                
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
