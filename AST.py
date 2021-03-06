from VM import *


class AST (object):
    current_scope = {}
    scope_stack = []
    func_table = {}
    current_emitted_function = ""

    def __init__(self):
        pass

    def emit(self, vm):
        pass


class RootNode(AST):

    def __init__(self, nodes, args=None, names=None):
        self._nodes = nodes
        self._args = args
        self._names = names

    def emit(self, vm):
        for i in self._nodes:
            i.emit(vm)


class FileHandleNode(AST):

    def __init__(self, val, in_loop):
        self._val = val
        self._in_loop = in_loop
        
    def emit(self, vm):
        vm.append_instruction(Instruction("DO FILEHANDLE", [ self._val, self._in_loop ]))
        
class BackTicksNode(AST):

    def __init__(self, cmdstr):
        self._cmdstr = cmdstr
        
    def emit(self, vm):
        vm.append_instruction(Instruction("DO BACKTICKS", [ self._cmdstr ]))

class InterpolatedValueNode(AST):

    def __init__(self, val):
        self._val = val
        
    def emit(self, vm):
        vm.append_instruction(Instruction("PUSH INTERP CONST", [ self._val ]))

class ValueNode(AST):

    def __init__(self, val):
        self._val = val

    def emit(self, vm):
        vm.append_instruction(Instruction("PUSH CONST", [ self._val ]))
        
class AnonListNode(AST):

    def __init__(self, val):
        self._arry = val

    def emit(self, vm):
        for i in self._arry:
            i.emit(vm)
        vm.append_instruction(Instruction("PUSH ANON LIST", [ len(self._arry) ]))

class ReturnNode(AST):

    def __init__(self, expr):
        self._expr = expr

    def emit(self, vm):
        if self._expr is not None:
            self._expr.emit(vm)
            vm.AppendInstruction(Instruction("RET", [True]))
        else:
            vm.AppendInstruction(Instruction("RET", [False]))

class LogicalOpNode(AST):

    def __init__(self, op, left, right):
        self._op = str(op)
        self._left = left
        self._right = right

    def emit(self, vm):
        if (self._op == '&&'):
            self._left.emit(vm)
            branch_anchor = vm.get_current_address()
            vm.append_instruction(Instruction("BZ", [None])) # fill this in later
            self._right.emit(vm)
            go_to_end = vm.get_current_address()
            vm.append_instruction(Instruction("JMP", [None]))
            location = vm.get_current_address()
            vm.append_instruction(Instruction("PUSH CONST", [Value(0)]))
            vm.pgm_stack[branch_anchor].args = [ location ]
            location = vm.get_current_address()
            vm.pgm_stack[go_to_end].args = [ location ]
        else:
            self._left.emit(vm)
            branch_anchor = vm.get_current_address()
            vm.append_instruction(Instruction("BNZ", [None])) # fill this in later
            self._right.emit(vm)
            go_to_end = vm.get_current_address()
            vm.append_instruction(Instruction("JMP", [None]))
            location = vm.get_current_address()
            vm.append_instruction(Instruction("PUSH CONST", [Value(1)]))
            vm.pgm_stack[branch_anchor].args = [ location ]
            location = vm.get_current_address()
            vm.pgm_stack[go_to_end].args = [ location ]

class BinOpNode(AST):

    def __init__(self, left, op, right):
        self._left = left
        self._op = op
        self._right = right

    def emit(self, vm):
        self._left.emit(vm)
        self._right.emit(vm)
        vm.append_instruction(Instruction("BINOP", [str(self._op)]))


class UnOpNode(AST):

    def __init__(self, op, v):
        self._op = op
        self._v = v

    def emit(self, vm):
        self._v.emit(vm)
        vm.append_instruction(Instruction("UNOP", [str(self._op)]))

class LabelNode(AST):

    def __init__(self, name):
        self._name = name
        
    def emit(self, vm):
        vm.append_instruction(Instruction("LABEL", [self._name]))

class BuiltInFunctionNode(AST):

    def __init__(self, name, fh, args):
        self._name = name
        self._fh = fh
        self._args = args

    def emit(self, vm):
        for i in self._args:
            i.emit(vm)
        vm.append_instruction(Instruction("CALL", [self._name, self._fh, len(self._args)]))
        
class FuncCallNode(AST):

    def __init__(self, name, args):
        self._name = name
        self._args = args

    def emit(self, vm):
        for i in self._args:
            i.emit(vm)
        
        # push the scope .. but VM will only preserve @_
        # since Perl 1 doesn't really have scopes
        vm.append_instruction(Instruction("PUSH SCOPE", []))
        vm.append_instruction(Instruction(
            "LIST ASSIGN", ['_', len(self._args) ]))
        vm.create_new_pgm_stack()
        AST.func_table[self._name].emit(vm);
        vm.save_pgm_stack(self._name);
        vm.restore_pgm_stack();
        vm.append_instruction(Instruction("CALLUSER", [self._name ]))
        vm.append_instruction(Instruction("POP SCOPE", []))
        
class MatchNode(AST):

    def __init__(self, name, index_expr, match_spec, invert=False):
        self._name = name
        self._expr = index_expr
        self._spec = match_spec
        self._invert = invert
    
    def emit(self, vm):
        has_expr = False
        if (self._expr != None):
            self._expr.emit(vm)
            has_expr = True
            
        if self._name == None:
            self._name = '_'
           
        vm.append_instruction(Instruction("DO MATCH", [ self._name, has_expr, self._spec, self._invert ]))
        
class TransNode(AST):

    def __init__(self, name, index_expr, trans_spec, invert=False):
        self._name = name
        self._expr = index_expr
        self._spec = trans_spec
        self._invert = invert
    
    def emit(self, vm):
        has_expr = False
        if (self._expr != None):
            self._expr.emit(vm)
            has_expr = True
            
        if self._name == None:
            self._name = '_'
           
        vm.append_instruction(Instruction("DO TRANS", [ self._name, has_expr, self._spec, self._invert ]))
        
class SubsNode(AST):

    def __init__(self, name, index_expr, subs_spec, invert):
        self._name = name
        self._expr = index_expr
        self._spec = subs_spec
        self._invert = invert
    
    def emit(self, vm):
        has_expr = False
        if (self._expr != None):
            self._expr.emit(vm)
            has_expr = True
            
        if self._name == None:
            self._name = '_'
           
        vm.append_instruction(Instruction("DO SUBS", [ self._name, has_expr, self._spec, self._invert ]))

class IndexNode(AST):

    def __init__(self, expr):
        self._expr = expr
        
    def emit(self, vm):
        self._expr.emit(vm)
        vm.append_instruction(Instruction("INDEX VAR"), [ None ])
        
class IfNode(AST):

    def __init__(
            self,
            cond,
            if_body,
            else_if_conds,
            else_if_bodies,
            else_body,
            invert_logic):
        self._cond = cond
        self._if_body = if_body
        self._else_if_conds = else_if_conds
        self._else_if_bodies = else_if_bodies
        self._else_body = else_body
        self._invert_logic = invert_logic

    def emit(self, vm):
        jmp_addresses = []
        self._cond.emit(vm)
        if (self._invert_logic):
            vm.append_instruction(Instruction("UNOP", [ "!" ]))
        branch_anchor = vm.get_current_address()
        vm.append_instruction(Instruction("BZ", [None]))        
        for i in self._if_body:
            i.emit(vm)
        jmp_addresses.append(vm.get_current_address())
        vm.append_instruction(Instruction("JMP", [None]))
        if_clause_anchor = vm.get_current_address()

        # populate the BZ jump address
        vm.pgm_stack[branch_anchor] = Instruction("BZ", [if_clause_anchor])
        if len(self._else_if_conds) > 0:
            for i in range(0, len(self._else_if_conds)):
                self._else_if_conds[i].emit(vm)
                else_if_anchor = vm.get_current_address()
                vm.append_instruction(Instruction("BZ", [None]))
                for j in self._else_if_bodies[i]:
                    j.emit(vm)
                jmp_addresses.append(vm.get_current_address())
                vm.append_instruction(Instruction("JMP", [None]))
                else_if_clause_anchor = vm.get_current_address()
                vm.pgm_stack[else_if_anchor] = Instruction(
                    "BZ", [else_if_clause_anchor])

        # do the else clause now
        for else_clause in self._else_body:
            else_clause.emit(vm)

        # go back and populate our JMPs since we know where the IF clause ends
        # now...
        end_of_if_address = vm.get_current_address()
        for i in jmp_addresses:
            vm.pgm_stack[i] = Instruction("JMP", [end_of_if_address])
            
class TernaryNode(AST):

    def __init__(
            self,
            true_expr, false_expr):
        self._true = true_expr
        self._false = false_expr

    def emit(self, vm):
       initial = vm.get_current_address()
       vm.append_instruction(Instruction("BZ", [None]))    
       self._true.emit(vm)
       true_jmp = vm.get_current_address()
       vm.append_instruction(Instruction("JMP", [None]))
       end_true = vm.get_current_address()
       vm.pgm_stack[initial] = Instruction("BZ", [ end_true ])
       self._false.emit(vm)
       end_false = vm.get_current_address()
       vm.pgm_stack[true_jmp] = Instruction("JMP", [ end_false ])
       
class ForNode(AST):

    def __init__(self, initial, cond, end_expr, body, name):
        self._initial = initial
        self._cond = cond
        self._end_expr = end_expr
        self._body = body
        self._name = name
        
    def emit(self, vm):
        if self._initial != None:
            self._initial.emit(vm)
        address_anchor = vm.get_current_address()
        if self._cond != None:
            self._cond.emit(vm)
            branch_anchor = vm.get_current_address()
            vm.append_instruction(Instruction("BZ", [ None ]))
        start_of_code = vm.get_current_address()
        for i in self._body:
            i.emit(vm)
        if self._end_expr != None:
            self._end_expr.emit(vm)
        vm.append_instruction(Instruction("LABEL", [ "CONTINUE_LOOP", start_of_code, self._name ]))
        vm.append_instruction(Instruction("JMP", [address_anchor]))
        vm.append_instruction(Instruction("LABEL", [ "END_LOOP", self._name ]))
        if self._cond != None:
            vm.pgm_stack[branch_anchor] = Instruction("BZ", [vm.get_current_address()])


class WhileNode(AST):

    def __init__(self, expr, body, continue_body, invert_logic, name):
        self._expr = expr
        self._body = body
        self._continue_body = continue_body
        self._invert_logic = invert_logic
        self._name = name

    def emit(self, vm):
        address_anchor = vm.get_current_address()
        self._expr.emit(vm)
        if (self._invert_logic):
            vm.append_instruction(Instruction("UNOP", [ "!" ]))
        branch_anchor = vm.get_current_address()
        vm.append_instruction(Instruction("BZ", [ None ]))
        start_of_code = vm.get_current_address()
        for i in self._body:
            i.emit(vm)
        vm.append_instruction(Instruction("LABEL", [ "CONTINUE_LOOP", start_of_code, self._name ]))
        for i in self._continue_body:
            i.emit(vm)
        vm.append_instruction(Instruction("JMP", [address_anchor]))
        vm.append_instruction(Instruction("LABEL", [ "END_LOOP", self._name ]))
        vm.pgm_stack[branch_anchor] = Instruction("BZ", [vm.get_current_address()])
        
class DoWhileNode(AST):
    
    def __init__(self, do_body, expr):
        self._do_body = do_body
        self._expr = expr
        
    def emit(self, vm):
        address_anchor = vm.get_current_address()
        for i in self._do_body:
            i.emit(vm)
        self._expr.emit(vm)
        branch_anchor = vm.get_current_address()
        vm.append_instruction(Instruction("BZ", [ None ]))
        vm.append_instruction(Instruction("LABEL", [ "CONTINUE_LOOP" ]))
        vm.append_instruction(Instruction("JMP", [ address_anchor ]))
        vm.append_instruction(Instruction("LABEL", [ "END_LOOP" ]))
        vm.pgm_stack[branch_anchor] = Instruction("BZ", [ vm.get_current_address() ])
        
class DoStatementNode(AST):
    
    def __init__(self, do_body):
        self._do_body = do_body
        
    def emit(self, vm):
        for i in self._do_body:
            i.emit(vm)
        
        
class LastNode(AST):
    
    def __init__(self, name=None):
        self._name = name
        
    def emit(self, vm):
        vm.append_instruction(Instruction("GOTO END LOOP", [ self._name ]))
        
class NextNode(AST):

    def __init__(self, name=None):
        self._name = name
    
    def emit(self, vm):
        vm.append_instruction(Instruction("GOTO CONTINUE LOOP", [ self._name ]))
        
class RedoNode(AST):

    def __init__(self, name=None):
        self._name = name
    
    def emit(self, vm):
        vm.append_instruction(Instruction("GOTO REDO LOOP", [ self._name ]))
        
class GotoNode(AST):

    def __init__(self, name=None):
        self._name = name
    
    def emit(self, vm):
        vm.append_instruction(Instruction("GOTO", [ self._name ]))

class IndexVar(AST):

    def __init__(self, expr):
        self._expr = expr

    def emit(self, vm):
        self._expr.emit(vm)
        vm.append_instruction(Instruction("INDEX VAR", []))

class ListMaxIndexNode(AST):
    
    def __init__(self, name):
        self._name = name
        
    def emit(self, vm):
        vm.append_instruction(Instruction("PUSH LIST MAX INDEX", [ self._name ]))

class ScalarVarNode(AST):

    def __init__(self, name, index_expr):
        self._name = name
        self._index_expr = index_expr

    def emit(self, vm):   
        if (self._index_expr != None):
            self._index_expr.emit(vm)
            
        vm.append_instruction(Instruction("PUSH SCALAR VAR",
            [ self._name, True if self._index_expr != None else False ]))

class HashVarNode(AST):

    def __init__(self, name):
        self._name = name
        
    def emit(self, vm):
        vm.append_instruction(Instruction("PUSH HASH VAR",
            [ self._name ] ))
            
class ListVarNode(AST):

    def __init__(self, name):
        self._name = name

    def emit(self, vm):    
        vm.append_instruction(Instruction("PUSH LIST VAR",
            [self._name, False]))

class ListAssignNode(AST):

    def __init__(self, name, arry):
        self._name = name
        self._arry = arry
        
    def emit(self, vm):
        # assigning a scalar in list context, just take first elemt
        if not (type(self._arry) is list):
            self._arry[0].emit(vm)
        else:
            for i in self._arry:
                i.emit(vm)
        vm.append_instruction(Instruction(
            "LIST ASSIGN", [self._name, len(self._arry) ]))
            
class UnpackAssignNode(AST):

    def __init__(self, vars, rval):
        self._vars = vars
        self._rval = rval
        
    def emit(self, vm): 
        # emit the rval first so we can feast off of it
        # but reverse it first.  
        self._rval.reverse()
        for i in self._rval:
            i.emit(vm)
            
        vm.append_instruction(Instruction("MULTI ASSIGN", [ self._vars, len(self._rval) ]))
            
class ScalarIncrDecrNode(AST):

    def __init__(self, name, expr, rvalue, op):
        self._name = name
        self._expr = expr
        self._rval = rvalue
        self._op = op
        
    def emit(self, vm):
        if (self._op == '+='):
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            self._rval.emit(vm)
            vm.append_instruction(Instruction("BINOP", [str('+')]))
            vm.append_instruction(Instruction("SCALAR ASSIGN", [ self._name, has_idx ]))
            
        elif (self._op == 'x='):
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            self._rval.emit(vm)
            vm.append_instruction(Instruction("BINOP", [str('x')]))
            vm.append_instruction(Instruction("SCALAR ASSIGN", [ self._name, has_idx ]))
            
        elif (self._op == '-='):
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            self._rval.emit(vm)
            vm.append_instruction(Instruction("BINOP", [str('-')]))
            vm.append_instruction(Instruction("SCALAR ASSIGN", [ self._name, has_idx ]))
            
        elif (self._op == '*='):
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            self._rval.emit(vm)
            vm.append_instruction(Instruction("BINOP", [str('*')]))
            vm.append_instruction(Instruction("SCALAR ASSIGN", [ self._name, has_idx ]))
            
        elif (self._op == '/='):
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            self._rval.emit(vm)
            vm.append_instruction(Instruction("BINOP", [str('/')]))
            vm.append_instruction(Instruction("SCALAR ASSIGN", [ self._name, has_idx ]))
            
        elif (self._op == '^='):
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            self._rval.emit(vm)
            vm.append_instruction(Instruction("BINOP", [str('^')]))
            vm.append_instruction(Instruction("SCALAR ASSIGN", [ self._name, has_idx ]))
            
        elif (self._op == '++'): # prefix ++
            self._name = self._expr._name
            if self._expr._index_expr:
                self._expr._index_expr.emit(vm)
            self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH CONST", [Value(1)]))
            vm.append_instruction(Instruction("BINOP", [str('+')]))
            vm.append_instruction(Instruction("SCALAR ASSIGN",
                [ self._name, True if self._expr._index_expr != None else False ]))
                
        elif (self._op == '--'): # prefix --
            self._name = self._expr._name
            if self._expr._index_expr:
                self._expr._index_expr.emit(vm)
            self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH CONST", [Value(1)]))
            vm.append_instruction(Instruction("BINOP", [str('-')]))
            vm.append_instruction(Instruction("SCALAR ASSIGN",
                [ self._name, True if self._expr._index_expr != None else False ]))
                
        # TODO: Major hack alert
        elif (self._op == 'post++'): # postfix ++
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            vm.append_instruction(Instruction("PUSH CONST", [ Value(1) ]))
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("INCR SCALAR", [ self._name, has_idx ]))
            if self._rval:
                #vm.append_instruction(Instruction("POP", []))
                self._rval._right.emit(vm)
                vm.append_instruction(Instruction("BINOP", [ str(self._rval._op) ]))
         
        # TODO: Major hack alert         
        elif (self._op == 'post--'): # postfix --
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            vm.append_instruction(Instruction("PUSH CONST", [ Value(1) ]))
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("DECR SCALAR", [ self._name, has_idx ]))
            if self._rval:
                vm.append_instruction(Instruction("POP", []))
                self._rval._right.emit(vm)
                vm.append_instruction(Instruction("BINOP", [ str(self._rval._op) ]))
            
        elif (self._op == '.='):
            has_idx = False
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("PUSH SCALAR VAR", [ self._name, has_idx ]))
            self._rval.emit(vm)
            if self._expr:
                has_idx = True
                self._expr.emit(vm)
            vm.append_instruction(Instruction("STR CAT", [ self._name, has_idx ]))
            # self._expr.emit(vm)
            # vm.append_instruction(Instruction("STR CAT", [ self._name, False ]))
            
            

class ScalarAssignNode(AST):
    
    def __init__(self, name, expr, index_expr):
        self._name = name
        self._expr = expr
        self._index_expr = index_expr

    def emit(self, vm):
        if (self._index_expr != None):
            self._index_expr.emit(vm)
            
        if (type(self._expr) is list):
            # assigning list in scalar context, emit last element
            self._expr[-1].emit(vm)

        else:
            # an actual scalar value assigned to something
            self._expr.emit(vm)

        vm.append_instruction(Instruction("SCALAR ASSIGN", [ self._name, True if self._index_expr != None else False ]))
