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


class ValueNode(AST):

    def __init__(self, val):
        self._val = val

    def emit(self, vm):
        vm.append_instruction(Instruction("PUSH CONST", [self._val]))


class ReturnNode(AST):

    def __init__(self, expr):
        self._expr = expr

    def emit(self, vm):
        if self._expr is not None:
            self._expr.emit(vm)
            vm.AppendInstruction(Instruction("RET", [True]))
        else:
            vm.AppendInstruction(Instruction("RET", [False]))


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


class UserFunctionNode(AST):

    def __init__(self, name, args):
        self._name = name
        self._args = args

    def emit(self, vm):
        pass


class BuiltInFunctionNode(AST):

    def __init__(self, name, args):
        self._name = name
        self._args = args

    def emit(self, vm):
        for i in self._args:
            i.emit(vm)
            vm.append_instruction(Instruction(
                "CALL", [self._name, len(self._args)]))


class IfNode(AST):

    def __init__(
            self,
            cond,
            if_body,
            else_if_conds,
            else_if_bodies,
            else_body):
        self._cond = cond
        self._if_body = if_body
        self._else_if_conds = else_if_conds
        self._else_if_bodies = else_if_bodies
        self._else_body = else_body

    def emit(self, vm):
        jmp_addresses = []
        self._cond.emit(vm)
        branch_anchor = vm.get_current_address()
        vm.append_instruction(Instruction("BZ", None))
        for i in self._if_body:
            i.emit(vm)
        jmp_addresses.append(vm.get_current_address())
        vm.append_instruction(Instruction("JMP", None))
        if_clause_anchor = vm.get_current_address()

        # populate the BZ jump address
        vm.pgm_stack[branch_anchor] = Instruction("BZ", [if_clause_anchor])
        if len(self._else_if_conds) > 0:
            for else_if_cond in self._else_if_conds:
                else_if_cond.emit(vm)
                else_if_anchor = vm.get_current_address()
                vm.append_instruction(Instruction("BZ", None))
                for j in else_if_cond:
                    j.emit(vm)
                jmp_addresses.append(vm.get_current_address())
                vm.append_instruction(Instruction("JMP", None))
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


class WhileNode(AST):

    def __init__(self, expr, body):
        self._expr = expr
        self._body = body

    def emit(self, vm):
        address_anchor = vm.get_current_address()
        self._expr.emit(vm)
        branch_anchor = vm.get_current_address()
        vm.append_instruction(Instruction("BZ", None))
        for i in self._body:
            i.emit(vm)
        vm.append_instruction(Instruction("JMP", [address_anchor]))
        vm.pgm_stack[branch_anchor] = Instruction(
            "BZ", [vm.get_current_address()])


class IndexVar(AST):

    def __init__(self, expr):
        self._expr = expr

    def emit(self, vm):
        self._expr.emit(vm)
        vm.append_instruction(Instruction("INDEX VAR", []))


class VarNode(AST):

    def __init__(self, name):
        self._name = name

    def emit(self, vm):
        vm.append_instruction(Instruction("PUSH VAR", [self._name]))


class AssignNode(AST):

    def __init__(self, name, context):
        self._name = name
        self._context = context

    def emit(self, vm):
        vm.append_instruction(Instruction(
            "ASSIGN", [self._name, self._context]))
