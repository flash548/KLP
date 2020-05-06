from AST import *
from TokenType import *


class Parser:
    def __init__(self, lexer):
        self.lineNumber = 1
        self.lex = lexer
        self.prev_token = Token(TokenType.NONE, Value(''))
        self.current_token = self.lex.get_next_token()
        self.statement_modifier_tokens = [ TokenType.IF, TokenType.UNLESS,
            TokenType.UNTIL, TokenType.WHILE ];
        self.last_label_name = None
        # used by spaceship op to tell whether to set $_ or not
        self.in_loop_expr = False

    def error(self):
        raise Exception("Invalid syntax on line: " + str(self.lineNumber))
        
    def is_an_operator(self, tok):
        return tok in [ TokenType.PLUS,
                    TokenType.MINUS,
                    TokenType.STR_CONCAT,
                    TokenType.LOGAND,
                    TokenType.LOGOR,
                    TokenType.LSHIFT,
                    TokenType.RSHIFT,
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
                    TokenType.MOD
        ]

    def parse(self):
        return expr()

    def eat(self, tokType):
        if self.current_token.type == tokType:
            if tokType == TokenType.NEWLINE:
                self.lineNumber += 1
            self.prev_token = self.current_token
            self.current_token = self.lex.get_next_token()
            # eat comments that in the midst of statements that straddle a new line
            while (self.current_token.type == TokenType.COMMENT 
                    and self.current_token.type != TokenType.EOF):
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
            stmts = []
            while (self.current_token.type != TokenType.RCURLY):
                stmts.append(self.statement())
                self.eat_end_of_statement()
            self.eat(TokenType.RCURLY)
            return RootNode(stmts)
            
        elif self.current_token.type == TokenType.LABEL:
            name = str(self.current_token.value)
            self.eat(TokenType.LABEL)
            if self.current_token.type in [ TokenType.WHILE, TokenType.UNTIL, TokenType.FOR ]:
                # no nothing for a labeled loop, we'll use the name later
                self.last_label_name = name
                return AST()
            # generic label statement
            return LabelNode(name)
            
        elif self.current_token.type == TokenType.LAST:
            self.eat(TokenType.LAST)
            label = None
            if self.current_token.type == TokenType.ID:
                label = str(self.current_token.value)
                self.eat(TokenType.ID)
            return self.check_for_conditional(LastNode(label))
            
        elif self.current_token.type == TokenType.NEXT:
            self.eat(TokenType.NEXT)
            label = None
            if self.current_token.type == TokenType.ID:
                label = str(self.current_token.value)
                self.eat(TokenType.ID)
            return self.check_for_conditional(NextNode(label))
            
        elif self.current_token.type == TokenType.REDO:
            self.eat(TokenType.REDO)
            label = None
            if self.current_token.type == TokenType.ID:
                label = str(self.current_token.value)
                self.eat(TokenType.ID)
            return self.check_for_conditional(RedoNode(label))
            
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
            return WhileNode(expr, [ node ], [], False, self.last_label_name)
        elif (self.current_token.type == TokenType.UNTIL):
            self.eat(TokenType.UNTIL)
            expr = self.expression();
            return WhileNode(expr, [ node ], [], True, self.last_label_name)
        else:
            return node
    
    def assignment(self):
    
        # look ahead to make sure this is an assignment statement
        self.lex.anchor() # insurance policy 
        isAssign = False
        found_lparen = False
        found_lparen_cnt = 0
        found_comma = False
        tok = self.current_token
        while (tok.type != TokenType.SEMICOLON and tok.type != TokenType.EOF):
            if (tok.type == TokenType.COMMA):
                found_comma = True
            if (tok.type in [TokenType.SCALAR, TokenType.LIST, TokenType.HASH]
                    and self.prev_token.type == TokenType.LPAREN):
                found_lparen_cnt += 1
                found_lparen = True
            if (tok.type == TokenType.RPAREN):
                found_lparen_cnt -= 1 # cxl out last lparen
            if (tok.type == TokenType.ASSIGN):
                # this is an assign statement
                found_lparen = (found_lparen and found_lparen_cnt == 0)
                isAssign = True
                break
            self.prev_token = tok
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
            self.in_loop_expr = True
            cond = self.statement()
            self.in_loop_expr = False
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
        fnode = ForNode(initial, cond, end, body, self.last_label_name)
        #self.last_label_name = None
        return fnode

    def while_statement(self):
        if (self.current_token.type == TokenType.UNTIL):
            self.eat(TokenType.UNTIL)
            invert_logic = True
        else:
            self.eat(TokenType.WHILE)
            invert_logic = False
        self.eat(TokenType.LPAREN)
        
        self.in_loop_expr = True
        expr = self.statement()
        self.in_loop_expr = False
        
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
        wnode = WhileNode(expr, while_clause, continue_clause, invert_logic, self.last_label_name)
        #self.last_label_name = None
        return wnode

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
            self.in_loop_expr = True
            expr = self.statement()
            self.in_loop_expr = False
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
            encased_curly = False
            if self.current_token.type == TokenType.LCURLY:
                encased_curly = True
                self.eat(TokenType.LCURLY)
                
            name = str(self.current_token.value) # the actual var's name
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
                
            if encased_curly:
                # has to have a RCURLY if we did ${a} syntax
                if self.current_token.type != TokenType.RCURLY:  
                    raise Exception("Parse Error: expected closing RCURLY on var!")
                self.eat(TokenType.RCURLY)
                
            if (self.current_token.type == TokenType.ASSIGN):
                self.eat(TokenType.ASSIGN)
                
                if (self.current_token.type == TokenType.LPAREN):
                    # array element assignment (or hash element)
                    return ScalarAssignNode(name, self.consume_list(), index_expr)
                else:
                    # regular scalar variable assignment
                    return ScalarAssignNode(name, self.expression(), index_expr)
            
            elif (self.current_token.type in [ TokenType.MATCH, TokenType.NOT_MATCH]):
                invert = False
                if self.current_token.type == TokenType.MATCH:
                    self.eat(TokenType.MATCH)
                else:
                    self.eat(TokenType.NOT_MATCH)
                    invert = True
                    
                if self.current_token.type == TokenType.MATCH_SPEC:
                    spec = self.current_token.value
                    self.eat(TokenType.MATCH_SPEC)
                    return MatchNode(name, index_expr, spec, invert)
                elif (self.current_token.type == TokenType.TRANS_SPEC):
                    spec = self.current_token.value
                    self.eat(TokenType.TRANS_SPEC)
                    return TransNode(name, index_expr, spec, invert)
                elif (self.current_token.type == TokenType.SUBS_SPEC):
                    spec = self.current_token.value
                    self.eat(TokenType.SUBS_SPEC)
                    return SubsNode(name, index_expr, spec, invert)
                else:
                    raise Exception ("Parser Error in / / expression!")
            
            elif (self.current_token.type == TokenType.INCR):
                self.eat(TokenType.INCR)
                return ScalarIncrDecrNode(name, index_expr, self.expression(), '+=')
                
            elif (self.current_token.type == TokenType.DECR):
                self.eat(TokenType.DECR)
                return ScalarIncrDecrNode(name, index_expr, self.expression(), '-=')
                
            elif (self.current_token.type == TokenType.MUL_INCR):
                self.eat(TokenType.MUL_INCR)
                return ScalarIncrDecrNode(name, index_expr, self.expression(), '*=')
                
            elif (self.current_token.type == TokenType.DIV_INCR):
                self.eat(TokenType.DIV_INCR)
                return ScalarIncrDecrNode(name, index_expr, self.expression(), '/=')
                
            elif (self.current_token.type == TokenType.XOR_INCR):
                self.eat(TokenType.XOR_INCR)
                return ScalarIncrDecrNode(name, index_expr, self.expression(), '^=')
                
            elif (self.current_token.type == TokenType.STR_INCR):
                self.eat(TokenType.STR_INCR)
                return ScalarIncrDecrNode(name, index_expr, self.expression(), '.=')
                
            elif (self.current_token.type == TokenType.PLUSPLUS):
                self.eat(TokenType.PLUSPLUS)
                return ScalarIncrDecrNode(name, index_expr, None, 'post++')
                
            elif (self.current_token.type == TokenType.MINUSMINUS):
                self.eat(TokenType.MINUSMINUS)
                return ScalarIncrDecrNode(name, index_expr, None, 'post--')
                
            else:
                return ScalarVarNode(name, index_expr)
        
        # handle a Match spec by itself - on the $_ var
        elif (token.type == TokenType.MATCH_SPEC):
            spec = self.current_token.value
            self.eat(TokenType.MATCH_SPEC)
            return MatchNode(None, None, spec, False)
        
        # handle a Transliteration spec by itself - on the $_ var        
        elif (token.type == TokenType.TRANS_SPEC):
            spec = self.current_token.value
            self.eat(TokenType.TRANS_SPEC)
            return TransNode(None, None, spec, False)
            
        # handle a Substitution spec by itself - on the $_ var        
        elif (token.type == TokenType.SUBS_SPEC):
            spec = self.current_token.value
            self.eat(TokenType.SUBS_SPEC)
            return SubsNode(None, None, spec, False)
        
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
                
        # '$#" 'twigil' (hat tip to p6)
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
            expr = self.expression()
            # expr should be of type 'ScalarVarNode'
            if not type(expr) is ScalarVarNode:
                raise Exception("Parse error: Prefix ++ expects variable lvalue")
            return ScalarIncrDecrNode(None, expr, None, '++')
            
        elif (token.type == TokenType.MINUSMINUS):
            # prefix decr
            self.eat(TokenType.MINUSMINUS)
            expr = self.expression()
            # expr should be of type 'ScalarVarNode'
            if not type(expr) is ScalarVarNode:
                raise Exception("Parse error: Prefix -- expects variable lvalue")
            return ScalarIncrDecrNode(None, expr, None, '--')
            
        elif (token.type == TokenType.ID):
            name = token.value
            self.eat(TokenType.ID)
            if (str(name) in TokenType.BUILTINS):
                # its a builtin - there are some special cases
                if (str(name) == 'print'
                        and self.current_token.type == TokenType.ID
                        and str(self.current_token.value) not in TokenType.BUILTINS):
                    # must be a FILEHANDLE BAREWORD
                    fh = str(self.current_token.value)
                    self.eat(TokenType.ID)
                    args = self.consume_list()
                    return BuiltInFunctionNode(name, fh, args)
                
                # shift is special since its destructive, don't eval the array arg
                # which is easy since it only takes one arg
                elif (str(name) == 'shift'):
                    eat_paren = False
                    if (self.current_token.type == TokenType.LPAREN):
                        self.eat(TokenType.LPAREN)
                        eat_paren = True
                    self.eat(TokenType.LIST)
                    var_name = self.current_token.value
                    self.eat(TokenType.ID)
                    if (eat_paren):
                        self.eat(TokenType.RPAREN)
                    return BuiltInFunctionNode(name, None, [ValueNode(var_name)])
                # shift is special since its destructive, don't eval the array arg
                # which is easy since it only takes one arg
                elif (str(name) == 'unshift'):
                    eat_paren = False
                    if (self.current_token.type == TokenType.LPAREN):
                        self.eat(TokenType.LPAREN)
                        eat_paren = True
                    self.eat(TokenType.LIST)
                    var_name = self.current_token.value
                    self.eat(TokenType.ID)
                    if (self.current_token.type == TokenType.COMMA):
                        self.eat(TokenType.COMMA)
                    else:
                        return BuiltInFunctionNode(name, None, [ValueNode(var_name), ValueNode(Value(None))])
                    
                    args = self.consume_list()
                    if (eat_paren):
                        self.eat(TokenType.RPAREN)
                    return BuiltInFunctionNode(name, None, [ValueNode(var_name)] + args)
                else:
                    args = self.consume_list()
                    return BuiltInFunctionNode(name, None, args)
            else:
                # its a BAREWORD, interp as string
                return ValueNode(str(name))
                
        elif (token.type == TokenType.SPACESHIP):
            self.eat(TokenType.SPACESHIP)
            return SpaceShipNode(token.value, self.in_loop_expr)
            
        elif (token.type == TokenType.BACKTICKS):
            self.eat(TokenType.BACKTICKS)
            return BackTicksNode(token.value)
                
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
                (not self.is_an_operator(self.current_token.type)) and
                (self.current_token.type not in self.statement_modifier_tokens)):
            list_elems.append(self.expression())
            if (self.current_token.type == TokenType.COMMA):
                self.eat(TokenType.COMMA)
        if (self.current_token.type not in self.statement_modifier_tokens):
            if (self.current_token.type == end_token and end_token != TokenType.SEMICOLON):
                self.eat(end_token)
        return list_elems
