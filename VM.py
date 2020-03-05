from Value import *


class Instruction:
    def __init__(self, opcode, args):
        self.opcode = opcode
        if (not (isinstance(args, list))):
            raise Exception("Instruction args must be a list!")
        self.args = args

    def __str__(self):
        s = self.opcode + ": "
        for i in self.args:
            s += str(i) + " "
        return s.strip()


class VM:
    def __init__(self):
        self.pgm_stack = []
        self.pgm_stack_frames = []
        self.pgm_frames = {}
        self.stack = []
        self.pc_stack = []
        self.pc = 0
        self.current_scope = {}
        self.scope_stack = []

    def get_variable(self, name):
        if name in self.current_scope:
            return self.current_scope[name]

        if len(self.scope_stack) > 0:
            for scp in self.scope_stack:
                if name in scp:
                    return scp[name]

        # if we get here, then no var was found
        raise Exception("Unknown var name: " + name)

    def var_exists(self, name):
        try:
            self.get_variable(name)
            return True
        except BaseException:
            return False

    def set_variable(self, name, val):
        if name in self.current_scope:
            self.current_scope[name] = val
        else:
            if len(self.scope_stack) > 0:
                for scp in self.scope_stack:
                    if name in scp:
                        scp[name] = val
            else:
                self.current_scope[name] = val

        def get_current_address(self):
            return len(self.pgm_stack)

    def append_instruction(self, i):
        self.pgm_stack.append(i)

    def create_new_pgm_stack(self):
        self.pgm_stack_frames.append(self.pgm_stack)
        self.pgm_stack = []

    def restore_pgm_stack(self):
        self.pgm_stack = self.pgm_stack_frames.pop()

    def save_pgm_stack(self, name):
        self.pgm_frames[name] = self.pgm_stack

    def dump_pgm_stack(self):
        print "PGM Stack:"
        for i in range(0, len(self.pgm_stack)):
            print str(self.pgm_stack[i])

    def dump_stack(self):
        print "Stack Dump: (length: %i)" % len(self.stack)
        for i in range(0, len(self.stack)):
            print str(self.stack[i])

    def run(self):
        while self.step():
            pass

    def step(self):
        if self.pc < len(self.pgm_stack):
            self.execute(self.pgm_stack[self.pc])
            self.pc += 1
            return True
        else:
            if len(self.pc_stack) != 0:
                self.stack.append(Value(True))
                self.pgm_stack = self.pgm_stack_frames.pop()
                self.pc = self.pc_stack.pop()
                self.current_scope = self.scope_stack.pop()
                return True

            return False  # no more code to execute

    def execute(self, instr):
        if (instr.opcode == "POP"):
            self.stack.pop()
        elif (instr.opcode == "BINOP"):
            self.perform_op(str(instr.args[0]))
        elif (instr.opcode == "UNOP"):
            self.perform_unop(str(instr.args[0]))
        elif (instr.opcode == "PUSH CONST"):
            self.stack.append(instr.args[0])
        elif (instr.opcode == "INDEX VAR"):
            self.perform_var_index(args[0])
        elif (instr.opcode == "PUSH VAR"):
            self.perform_push_var(str(instr.args[0]))
        elif (instr.opcode == "BZ"):
            if (not self.stack.pop()):
                self.pc = int(instr.args[0])
        elif (instr.opcode == "JMP"):
            self.pc = int(instr.args[0])
        elif (instr.opcode == "ASSIGN"):
            if (instr.args[1] == "SCALAR"):
                self.perform_scalar_assign(instr.args[0])
            elif (instr.args[1] == "LIST"):
                self.perform_list_assign(instr.args[0])
            elif (instr.args[1] == "HASH"):
                self.perform_list_assign(instr.args[0])
            else:
                raise Exception("Unknown context: " + instr.args[1])
        elif (instr.opcode == "CALLUSER"):
            self.perform_call_user_func(str(instr.args[0]))
        elif (instr.opcode == "CALL"):
            self.perform_func_call(str(instr.args[0]), instr.args[1])
        elif (instr.opcode == "RET"):
            self.perform_return(instr.args[0])
        else:
            raise Exception("Unknown Instruction: " + instr.opcode)

    def perform_op(self, op):
        _right = self.stack.pop()
        _left = self.stack.pop()

        if (op == '+'):
            self.stack.append(_left + _right)
        elif (op == '-'):
            self.stack.append(_left - _right)
        elif (op == '*'):
            self.stack.append(_left * _right)
        elif (op == '/'):
            self.stack.append(_left / _right)
        elif (op == '^'):
            self.stack.append(_left ^ _right)
        elif (op == '.'):
            self.stack.append(_left.str_concat(_right))
        elif (op == '%'):
            self.stack.append(_left % _right)
        elif (op == 'eq'):
            self.stack.append(_left.str_eq(_right))
        elif (op == 'ne'):
            self.stack.append(_left.str_ne(_right))
        elif (op == 'lt'):
            self.stack.append(_left.str_lt(_right))
        elif (op == 'le'):
            self.stack.append(_left.str_le(_right))
        elif (op == 'gt'):
            self.stack.append(_left.str_gt(_right))
        elif (op == 'ge'):
            self.stack.append(_left.str_ge(_right))
        elif (op == '=='):
            self.stack.append(_left == _right)
        elif (op == '!='):
            self.stack.append(_left != _right)
        elif (op == '<'):
            self.stack.append(_left < _right)
        elif (op == '<='):
            self.stack.append(_left <= _right)
        elif (op == '>'):
            self.stack.append(_left > _right)
        elif (op == '>='):
            self.stack.append(_left >= _right)
        elif (op == '&'):
            self.stack.append(_left & _right)
        elif (op == '|'):
            self.stack.append(_left | _right)
        elif (op == '<<'):
            self.stack.append(_left << _right)
        elif (op == '>>'):
            self.stack.append(_left >> _right)
        else:
            raise Exception("Invalid operation: " + op)

    def perform_unop(self, op):
        _left = self.stack.pop()

        if (op == '+'):
            self.stack.append(+_left)
        elif (op == '-'):
            self.stack.append(-_left)
        elif (op == '!'):
            self.stack.append(not _left)
        else:
            raise Exception("Invalid Unop: " + op)

    def perform_var_index(self):
        _index = self.stack.pop()
        _left = self.stack.pop()
        self.stack.append(_left[_index])

    def perform_push_var(self, name):
        self.stack.append(self.get_variable(name))

    def perform_call_user_func(self, name):
        if (name in self.pgm_frames):
            self.pgm_stack_frames.append(self.pgm_stack)
            self.pc_stack.append(self.pc)

            self.pgm_stack = self.pgm_frames[name]
            self.pc = 0

            self.scope_stack.append(self.current_scope)
            self.current_scope = {}
        else:
            raise Exception("Undefined sub: " + name)

    def perform_func_call(self, name):
        if (name == "print"):
            print str(self.stack.pop())
        else:
            raise Exception("Undefined built-in: " + name)

    def perform_scalar_assign(self, name):
        self.set_variable(name, self.stack.pop().scalar_context())

    def perform_list_assign(self, name):
        self.set_variable(name, self.stack.pop().list_context())

    def perform_hash_assign(self, name):
        self.set_variable(name, self.stack.pop().hash_context())