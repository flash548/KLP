from Value import *
from DataStack import DataStack
import sys

class Instruction:
    def __init__(self, opcode, args):
        self.opcode = opcode
        if (not (isinstance(args, list))):
            raise Exception("Instruction args must be a list! OPCODE: " + self.opcode)
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
        self.stack = DataStack(100)
        self.pc_stack = []
        self.pc = 0
        self.current_scope = {}  # place where we store variables
        self.scope_stack = []

    def get_variable(self, name):
        if name in self.current_scope:
            return self.current_scope[name]

        if len(self.scope_stack) > 0:
            for scope in self.scope_stack:
                if name in scope:
                    return scope[name]

        return Value(0)  # if we get here, autovivify in perl parlance...

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
        """ Dumps the current program stack to STDOUT """
        
        print "PGM Stack:"
        for i in range(0, len(self.pgm_stack)):
            print str(i) + ": " + str(self.pgm_stack[i])

    def dump_stack(self):
        """ Dumps the data stack to STDOUT for debugging """
        
        print "Stack Dump: (length: %i)" % len(self.stack)
        for i in range(0, len(self.stack)):
            print str(self.stack[i])
            
    def dump_current_scope(self):
        """ Dumps the variables in the current scope to STDOUT """
        
        print "Current Scope Dump:"
        for i in self.current_scope:
            print i + ": " + str(self.current_scope[i])
                
    def run(self):
        while self.step():
            pass

    def step(self):
        if self.pc < len(self.pgm_stack):
            self.execute(self.pgm_stack[self.pc])
            return True
        else:
            if len(self.pc_stack) != 0:
                self.stack.push(Value(True))
                self.pgm_stack = self.pgm_stack_frames.pop()
                self.pc = self.pc_stack.pop()
                #self.current_scope = self.scope_stack.pop()
                return True

            return False  # no more code to execute

    def execute(self, instr):
        self.pc += 1 # incr to next instruction, unless it gets mod'd in here
    
        if (instr.opcode == "POP"):
            self.stack.pop()
        elif (instr.opcode == "LABEL"):
            pass
        elif (instr.opcode == "BINOP"):
            self.perform_op(str(instr.args[0]))
        elif (instr.opcode == "UNOP"):
            self.perform_unop(str(instr.args[0]))
        elif (instr.opcode == "PUSH CONST"):
            self.stack.push(instr.args[0])
        elif (instr.opcode == "PUSH INTERP CONST"):
            self.perform_interpolated_push(instr.args[0])
        elif (instr.opcode == "INDEX VAR"):
            self.perform_var_index(args[0])
        elif (instr.opcode == "PUSH SCALAR VAR"):
            self.perform_push_var(str(instr.args[0]), instr.args[1], 'scalar')
        elif (instr.opcode == "PUSH LIST VAR"):
            self.perform_push_var(str(instr.args[0]), instr.args[1], 'list')
        elif (instr.opcode == "PUSH ANON LIST"):
            self.perform_push_anon_list(instr.args[0])
        elif (instr.opcode == "GOTO END LOOP"):
            self.go_to_label("END_LOOP")
        elif (instr.opcode == "GOTO CONTINUE LOOP"):
            self.go_to_label("CONTINUE_LOOP")
        elif (instr.opcode == "BNZ"):
            if (self.stack.pop().boolify()):
                self.pc = int(instr.args[0])
        elif (instr.opcode == "BZ"):
            if (not self.stack.pop().boolify()):
                self.pc = int(instr.args[0])
        elif (instr.opcode == "JMP"):
            self.pc = int(instr.args[0])
        elif (instr.opcode == "SCALAR ASSIGN"):
            self.perform_scalar_assign(instr.args[0], instr.args[1])
        elif (instr.opcode == "INCR SCALAR"):
            self.perform_incr_decr(instr.args[0], True)
        elif (instr.opcode == "DECR SCALAR"):
            self.perform_incr_decr(instr.args[0], False)
        elif (instr.opcode == "LIST ASSIGN"):
            self.perform_list_assign(instr.args[0], instr.args[1])
        elif (instr.opcode == "HASH ASSIGN"):
            self.perform_list_assign(instr.args[0])
        elif (instr.opcode == "CALLUSER"):
            self.perform_call_user_func(str(instr.args[0]))
        elif (instr.opcode == "CALL"):
            self.perform_func_call(str(instr.args[0]), instr.args[1])
        elif (instr.opcode == "CALLUSER"):
            self.perform_user_func_call(str(instr.args[0]))
        elif (instr.opcode == "RET"):
            self.perform_return(instr.args[0])
        else:
            raise Exception("Unknown Instruction: " + instr.opcode)
            
    def go_to_label(self, label):
        for i in range(self.pc, len(self.pgm_stack)):
            if self.pgm_stack[i].opcode == "LABEL" and self.pgm_stack[i].args[0] == label:
                self.pc = i
                return
        raise Exception("Could not find label: " + label)

    def perform_op(self, op):
        _right = self.stack.pop()
        _left = self.stack.pop()

        if (op == '+'):
            self.stack.push(_left + _right)
        elif (op == '-'):
            self.stack.push(_left - _right)
        elif (op == '*'):
            self.stack.push(_left * _right)
        elif (op == '/'):
            self.stack.push(_left / _right)
        elif (op == '^'):
            self.stack.push(_left ^ _right)
        elif (op == '.'):
            self.stack.push(_left.str_concat(_right))
        elif (op == '%'):
            self.stack.push(_left % _right)
        elif (op == 'eq'):
            self.stack.push(_left.str_eq(_right))
        elif (op == 'ne'):
            self.stack.push(_left.str_ne(_right))
        elif (op == 'lt'):
            self.stack.push(_left.str_lt(_right))
        elif (op == 'le'):
            self.stack.push(_left.str_le(_right))
        elif (op == 'gt'):
            self.stack.push(_left.str_gt(_right))
        elif (op == 'ge'):
            self.stack.push(_left.str_ge(_right))
        elif (op == '=='):
            self.stack.push(_left == _right)
        elif (op == '!='):
            self.stack.push(_left != _right)
        elif (op == '<'):
            self.stack.push(_left < _right)
        elif (op == '<='):
            self.stack.push(_left <= _right)
        elif (op == '>'):
            self.stack.push(_left > _right)
        elif (op == '>='):
            self.stack.push(_left >= _right)
        elif (op == '&'):
            self.stack.push(_left & _right)
        elif (op == '|'):
            self.stack.push(_left | _right)
        elif (op == '<<'):
            self.stack.push(_left << _right)
        elif (op == '>>'):
            self.stack.push(_left >> _right)
        else:
            raise Exception("Invalid operation: " + op)

    def perform_unop(self, op):
        _left = self.stack.pop()

        if (op == '+'):
            self.stack.push(+_left)
        elif (op == '-'):
            self.stack.push(-_left)
        elif (op == '!'):
            self.stack.push(Value(not _left.boolify()))
        else:
            raise Exception("Invalid Unop: " + op)

    def perform_var_index(self):
        _index = self.stack.pop()
        _left = self.stack.pop()
        self.stack.push(_left[_index].scalar_context())

    # name - variable name
    # index_expr - T/F if we're indexing this variable
    # context - scalar or list
    def perform_push_var(self, name, index_expr, context):
        v = self.get_variable(name)
        if (index_expr == True):
            v = v[int(self.stack.pop())]    
        if (context == 'scalar'):
            self.stack.push(v.scalar_context())
        elif (context == 'list'):
            self.stack.push(v.list_context())
        else:
            raise Exception("Unknown context!")
            
    def perform_interpolated_push(self, val):
        """ Interpolate this string before pushing as a const """
        
        string_const = str(val)
        vars = {}
        # look for sigils and get varnames
        i = 0
        in_curly = False
        in_var = False
        escaped = False
        varname = ""
        var_to_replace = ""
        while i < len(string_const):
            if (string_const[i] in ('$', '@', '%') and not escaped):
                in_var = True
                var_to_replace += string_const[i]
            elif (string_const[i] == '{' and in_var):
                in_curly = True
            elif (string_const[i] == '}' and in_curly):
                vars[var_to_replace] = varname
                varname = ""
                var_to_replace = ""
                in_var = False
                in_curly = False
            elif (string_const[i].isspace() and in_var and in_curly):
                raise Exception("Invalid variable string: " + varname)
            elif (string_const[i].isspace() and in_var):
                vars[var_to_replace] = varname
                varname = ""
                var_to_replace = ""
                in_var = False
            elif (in_var):
                var_to_replace += string_const[i]
                varname += string_const[i]

            i += 1
    
        # if we get here and we're 'in_curly' = True then syntax errpr
        if in_curly:
            raise Exception("Invalid variable string in string: " + varname)
        
        if in_var:
            vars[var_to_replace] = varname
            
        # now replace all the vars with their looked up values
        #  these resolves will be in scalar context as a string
        for var in vars:
            v = self.get_variable(vars[var])
            string_const = string_const.replace(var, str(v.scalar_context()))
                
        self.stack.push(Value(string_const))
        

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
            
    def perform_incr_decr(self, name, incr):
        v = self.get_variable(name)
        val = self.stack.pop()
        if (incr == True):
            v = v + val
        else:
            v = v - val
        self.set_variable(name, v)
            

    def perform_func_call(self, name, argslen):
        args = []
        for i in range(0, argslen):
            args.append(self.stack.pop())            
        
        if (name == "print"):
            sys.stdout.write(str(args[0]))
            self.stack.push(Value(1))
        else:
            raise Exception("Undefined built-in: " + name)
            
    def perform_user_func_call(self, name):
        if (name in self.pgm_frames):
            # store away current pgm stack and its pc
            self.pgm_stack_frames.append(self.pgm_stack)
            self.pc_stack.append(self.pc);

            # set current pgm stack to the stack from our user defined function hash
            self.pgm_stack = self.pgm_frames[name];
            self.pc = 0;  # reset the pc
        else:
            raise Exception("Unknown user function: " + name)

    def perform_scalar_assign(self, name, index_expr):
        v = self.get_variable(name)
        if (index_expr == True):
            val = self.stack.pop()
            idx = self.stack.pop()
            v[idx.numerify()] = val.scalar_context()
        else:
            v = self.stack.pop().scalar_context()
        self.set_variable(name, v)

    def perform_push_anon_list(self, length):
        arry = Value([])
        for i in range(0, length):
            arry.push(self.stack.pop())
        arry.reverse()
        self.stack.push(arry)

    def perform_list_assign(self, name, length):
        arry = Value([])
        for i in range(0, length):
            arry.push(self.stack.pop())
        arry.reverse()
        self.set_variable(name, arry)

    def perform_hash_assign(self, name):
        self.set_variable(name, self.stack.pop().hash_context())
