from VM import *

class AST (object):
    current_scope = { }
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
    
class ValueNode(AST):
    
    def __init__(self, val):
        self._val = val
        
    def emit(self, vm):
        vm.append_instruction(Instruction("PUSH CONST", [ self._val ]))
        
class ReturnNode(AST):
    
    def __init__(self, expr):
        self._expr = expr
        
    def emit(self, vm):
        if self._expr != None:
            self._expr.emit(vm)
            vm.AppendInstruction(Instruction("RET", [ True ]))
        else:
            vm.AppendInstruction(Instruction("RET", [ False ]))
            
class BinOpNode(AST):
    
    def __init__(self, left, op, right):
        self._left = left
        self._op = op
        self._right = right
        
    def emit(self, vm):
        self._left.emit(vm)
        self._right.emit(vm)
        vm.append_instruction(Instruction("BINOP", [ str(self._op) ]))
        
class AssignNode(AST):
    
    def __init__(self, name, expr, op):
        self._name = name
        self._expr = expr
        self._op = op
        
    def emit(self, vm):
        pass
        

        
        
        
