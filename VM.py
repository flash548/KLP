from Value import *
from DataStack import DataStack
from regexp_funcs import *
from builtin_funcs import BuiltIns
import sys, os


class Instruction:
    def __init__(self, opcode, args):
        self.opcode = opcode
        if (not (isinstance(args, list))):
            raise Exception("Instruction args must be a list! OPCODE: " + self.opcode)
        self.args = args
        self.last_fh_read = None

    def __str__(self):
        s = self.opcode + ": "
        for i in self.args:
            s += str(i) + " "
        return s.strip()


class VM:
    def __init__(self):
        self.pgm_stack = []
        self.pgm_stack_frames = []
        self.pgm_frames = {} # holds our subroutines (each being a separate pgm_stack)
        self.stack = DataStack(100)
        self.pc_stack = []
        self.pc = 0
        self.current_scope = {}  # place where we store variables
        self.scope_stack = []

    def get_variable(self, name, type):
        if type == 'scalar':
            name = '$' + name
        elif type == 'list':
            name = '@' + name
        elif type == 'hash':
            name = '%' + name
        elif type == 'raw':
            # for barewords
            pass
        else:
            raise Exception("unknown variable type in get_variable()")
            
        if name in self.current_scope:
            return self.current_scope[name]

        if len(self.scope_stack) > 0:
            for scope in self.scope_stack:
                if name in scope:
                    return scope[name]
        
        # if we get here, autovivify in perl parlance...
        if type == 'scalar':
            return Value(None)  
        elif type == 'list':
            return Value([])
        elif type == 'hash':
            return Value({})
        elif type == 'raw':
            return Value(None)
        

    def set_variable(self, name, val, type):
        if type == 'scalar':
            name = '$' + name
        elif type == 'list':
            name = '@' + name
        elif type == 'hash':
            name = '%' + name
        elif type == 'raw':
            # barewords
            pass
        else:
            raise Exception("unknown variable type in set_variable()")

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

    def dump_pgm_stack(self, name=None):
        """ Dumps the current program stack to STDOUT """
        
        if (name == None):
            print "PGM Stack:"
            for i in range(0, len(self.pgm_stack)):
                print str(i) + ": " + str(self.pgm_stack[i])
        else:
            if name in self.pgm_frames:
                print "PGM Stack named: " + name
                for i in range(len(self.pgm_frames[name])):
                    print str(i) + ": " + str(self.pgm_frames[name][i])
            else:
                print "No program frame exists by that name: " + name
                
        print ""

    def dump_stack(self):
        """ Dumps the data stack to STDOUT for debugging """
        
        print "Stack Dump: (length: %i)" % len(self.stack)
        for i in range(len(self.stack)-1, -1, -1):
            print str(self.stack[i])
            
        print ""
            
    def dump_current_scope(self):
        """ Dumps the variables in the current scope to STDOUT """
        
        print "Current Scope Dump:"
        for i in self.current_scope:
            print i + ": " + str(self.current_scope[i])
            
        print ""
                
    def run(self):

        # try:
        is_debug = True
        while self.step():
            # r = raw_input()
            # if (r == 'q'):
                # is_debug = False
                
            # if is_debug:
                # print "%s: %s\n" % (self.pc, self.pgm_stack[self.pc])
                # print self.dump_stack()
                # print self.dump_current_scope()
            pass
        # except Exception as e:
            # pass
            # exc_type, exc_obj, exc_tb = sys.exc_info()
            # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            # print(exc_type, fname, exc_tb.tb_lineno)

    def step(self):
        if self.pc < len(self.pgm_stack):
            self.execute(self.pgm_stack[self.pc])
            return True
        else:
            if len(self.pc_stack) != 0:
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
            
        elif (instr.opcode == "DO MATCH"):
            do_match_op(self, str(instr.args[0]), instr.args[1], instr.args[2], instr.args[3])
            
        elif (instr.opcode == "DO TRANS"):
            do_trans_op(self, str(instr.args[0]), instr.args[1], instr.args[2], instr.args[3])
            
        elif (instr.opcode == "DO SUBS"):
            do_subs_op(self, str(instr.args[0]), instr.args[1], instr.args[2], instr.args[3])
            
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
            self.go_to_loop_label("END_LOOP", instr.args[0])
            
        elif (instr.opcode == "GOTO CONTINUE LOOP"):
            self.go_to_loop_label("CONTINUE_LOOP", instr.args[0])
            
        elif (instr.opcode == "GOTO REDO LOOP"):
            self.go_to_loop_label("CONTINUE_LOOP", instr.args[0])
            
        elif (instr.opcode == "GOTO"):
            self.go_to_label(instr.args[0])
            
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
            
        elif (instr.opcode == "PUSH LIST MAX INDEX"):
            self.perform_get_list_max_index(instr.args[0])
            
        elif (instr.opcode == "STR CAT"):
            self.perform_string_cat(instr.args[0], instr.args[1])
            
        elif (instr.opcode == "INCR SCALAR"):
            self.perform_incr_decr(instr.args[0], instr.args[1], True)
            
        elif (instr.opcode == "DECR SCALAR"):
            self.perform_incr_decr(instr.args[0], instr.args[1], False)
            
        elif (instr.opcode == "LIST ASSIGN"):
            self.perform_list_assign(instr.args[0], instr.args[1])
            
        elif (instr.opcode == "CALLUSER"):
            self.perform_call_user_func(str(instr.args[0]))
            
        elif (instr.opcode == "CALL"):
            self.perform_func_call(str(instr.args[0]), instr.args[1], instr.args[2])
            
        elif (instr.opcode == "CALLUSER"):
            self.perform_user_func_call(str(instr.args[0]))
            
        elif (instr.opcode == "MULTI ASSIGN"):
            self.perform_multi_assign(instr.args[0], instr.args[1])
            
        elif (instr.opcode == "DO SPACESHIP"):
            self.perform_spaceship(instr.args[0], instr.args[1])
            
        elif (instr.opcode == "DO BACKTICKS"):
            self.perform_backticks(instr.args[0])

        else:
            raise Exception("Unknown Instruction: " + instr.opcode)
     
    def go_to_label(self, label):
    
        # search the full pgm stack (current one anyways)
        for i in range(0, len(self.pgm_stack)):
                if self.pgm_stack[i].opcode == "LABEL" and self.pgm_stack[i].args[0] == label:
                    self.pc = i
                    return
        
        
    def go_to_loop_label(self, label, loop_name):
        if loop_name == None:
            for i in range(self.pc, len(self.pgm_stack)):
                if self.pgm_stack[i].opcode == "LABEL" and self.pgm_stack[i].args[0] == label:
                    self.pc = i
                    return
        else:
            # find the "extreme last" occurence of loop name in the stack
            occurences = []
            if label == "CONTINUE_LOOP":
                for i in range(self.pc, len(self.pgm_stack)):
                    if (self.pgm_stack[i].opcode == "LABEL" 
                            and self.pgm_stack[i].args[0] == "CONTINUE_LOOP"
                            and self.pgm_stack[i].args[2] == loop_name):
                        occurences.append(i)
            elif label == "REDO_LOOP":
                for i in range(self.pc, len(self.pgm_stack)):
                    if (self.pgm_stack[i].opcode == "LABEL" 
                            and self.pgm_stack[i].args[0] == "CONTINUE_LOOP"
                            and self.pgm_stack[i].args[2] == loop_name):
                        occurences.append(self.pgm_stack[i].args[1])
            else:
                for i in range(self.pc, len(self.pgm_stack)):
                    if (self.pgm_stack[i].opcode == "LABEL" 
                            and self.pgm_stack[i].args[0] == label
                            and self.pgm_stack[i].args[1] == loop_name):
                        occurences.append(i)
                        
            if len(occurences) > 0:
                self.pc = occurences[-1]
                return
                
        raise Exception("Could not find label: " + label)
        
    def perform_spaceship(self, val, in_loop):
        v = self.get_variable(str(val), 'raw')
        self.last_fh_read = val
        l = None
        try:
            l = v._val.readline()
        except:
            pass
            
        # set the $_ if we're supposed to
        if (in_loop):
            self.set_variable('_', Value(l), 'scalar')
            
        if (l == ''):    
            self.stack.push(Value(''))
        else:
            self.stack.push(Value(l))
        
    def perform_backticks(self, cmdstr):
        self.perform_interpolated_push(cmdstr)

        # get interp'd value back
        interp_val = self.stack.pop()
        BuiltIns.do_backticks(self, interp_val)

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
            # catch the divide by zero possibility
            try:
                self.stack.push(_left / _right)
            except ZeroDivisionError as e:
                self.stack.push(Value(float('inf')))
        elif (op == '^'):
            self.stack.push(_left ^ _right)
        elif (op == '.'):
            self.stack.push(_left.str_concat(_right))
        elif (op == '%'):
            self.stack.push(_left % _right)
        elif (op == '=='):
            self.stack.push(_left == _right)
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
        elif (op == 'x'):
            self.stack.push(Value(_left.stringify() * int(_right.numerify())))
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
        if (index_expr == True):
            idx = self.stack.pop()
            if type(idx._val) is str:
                v = self.get_variable(name, 'hash')
                v = v[str(idx)] 
                self.stack.push(v.scalar_context())
            else:
                v = self.get_variable(name, 'list')
                v = v[int(idx)] 
                self.stack.push(v.scalar_context())
        else:
            if (context == 'list'):
                # expand out the list, and push all elems onto stack
                v = self.get_variable(name, context)
                self.stack.push(v.list_context())
            else:
                v = self.get_variable(name, context)
                self.stack.push(v.scalar_context())
       
    def perform_get_list_max_index(self, name):
        v = self.get_variable(name, 'list')
        self.stack.push(Value(len(v)-1))
            
    def perform_interpolated_push(self, val):
        """ Interpolate a string before pushing it onto stack as a const """
        
        string_const = str(val)
        vars = {}
        
        # look for sigils and get varnames
        # varnames can be encased in {} as well
        # so lots of fun in here!
        
        i = 0
        in_curly = False
        in_var = False
        escaped = False
        varname = ""
        var_to_replace = ""
        sigil = None
        while i < len(string_const):
            if (string_const[i] in ('$', '@') 
                    and not escaped 
                    and not in_var
                    and string_const[-1] not in ('$', '@') ):
                sigil = string_const[i]
                in_var = True
                if (i - 1 >= 0) and string_const[i-1] == '\\':
                    var_to_replace += '\\'
                var_to_replace += string_const[i]
            elif (string_const[i] == '{' and in_var):
                var_to_replace += '{'
                in_curly = True
            elif (string_const[i] == '}' and in_curly):
                var_to_replace += '}'
                vars[var_to_replace] = varname
                varname = ""
                var_to_replace = ""
                in_var = False
                in_curly = False
            elif (string_const[i].isspace() and in_var and in_curly):
                raise Exception("Invalid variable string: " + varname)
            elif ((not string_const[i].isalnum() and string_const[i] != '_') and in_var):
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
            sigil = var[0]
            var_kind = None
            if var[0] == '\\': 
                continue
            if sigil == '$': var_kind = 'scalar'
            elif sigil == '@': var_kind = 'list'
            #elif sigil == '%': var_kind = 'hash'
            
            v = self.get_variable(vars[var].replace('{', '').replace('}', ''), var_kind)
            string_const = re.sub("(?<!\\\\)\\"+var, str(v.scalar_context()), string_const)
         
        string_const = string_const.replace('\\$', '$')
        string_const = string_const.replace('\\@', '@')   
        self.stack.push(Value(string_const))
        

    def perform_call_user_func(self, name):
        if (name in self.pgm_frames):
            self.pgm_stack_frames.append(self.pgm_stack)
            self.pc_stack.append(self.pc)

            self.pgm_stack = self.pgm_frames[name]
            self.pc = 0

            #self.scope_stack.append(self.current_scope)
            #self.current_scope = {}
        else:
            raise Exception("Undefined sub: " + name)
            
    def perform_string_cat(self, name, idx_expr):
        idx = None
        if idx_expr:
            idx = self.stack.pop()
            
        incr_amt = self.stack.pop() # what were adding to the string
        lval = self.stack.pop() # what we're adding/subing to
        lval = lval.str_concat(incr_amt)

        # now decide where to stuff it back to    
        # see if its a list element or not
        if idx_expr:
            v = self.get_variable(name, 'list')
            v[idx.numerify()] = lval
            self.set_variable(name, v, 'list')
        else:
            self.set_variable(name, lval, 'scalar')
    
        self.stack.push(lval)
            
    def perform_incr_decr(self, name, idx_expr, incr):
        """ Performs the postfix incr/decr """
        
        idx = None
        lval = None
        if idx_expr:
            idx = self.stack.pop()
            lval = self.get_variable(name, 'list')
            lval = lval[idx.numerify()]
        else:
            lval = self.get_variable(name, 'scalar')
            
        incr_amt = self.stack.pop() # incr/decr amnt
        #lval = self.stack.pop() # what we're adding/subing to
        if incr == True:
            lval += incr_amt
        else:
            lval -= incr_amt
            
        # now decide where to stuff it back to    
        # see if its a list element or not
        if idx_expr:
            v = self.get_variable(name, 'list')
            v[idx.numerify()] = lval.scalar_context()
            self.set_variable(name, v, 'list')
        else:
            self.set_variable(name, lval, 'scalar')
            
        #self.stack.push(lval)
                        

    def perform_func_call(self, name, fh, argslen):
        args = []
        for i in range(0, argslen):
            args.append(self.stack.pop())            
        
        if (name == "print"): 
            # print may or may not have a FH with it
            BuiltIns.do_print(self, fh, args)
        elif (name == 'die'):
            BuiltIns.do_die(self, args)
        elif (name == 'length'):
            BuiltIns.do_length(self, args)
        elif (name == 'join'):
            BuiltIns.do_join(self, args)
        elif (name == 'keys'):
            BuiltIns.do_keys(self, args)
        elif (name == 'values'):
            BuiltIns.do_values(self, args)
        elif (name == 'each'):
            BuiltIns.do_each(self, args)
        elif (name == 'eval'):
            BuiltIns.do_eval(self, args)
        elif (name == 'open'):
            BuiltIns.do_open(self, args)
        elif (name == 'close'):
            BuiltIns.do_close(self, args)
        elif (name == 'eof'):
            BuiltIns.do_eof(self, args)
        elif (name == 'shift'):
            BuiltIns.do_shift(self, args)
        elif (name == 'unshift'):
            BuiltIns.do_unshift(self, args)
        elif (name == 'index'):
            BuiltIns.do_index(self, args)
        elif (name == 'sprintf'):
            BuiltIns.do_sprintf(self, args)
        elif (name == 'printf'):
            BuiltIns.do_printf(self, fh, args)
        elif (name == 'seek'):
            BuiltIns.do_seek(self, args)
        elif (name == 'tell'):
            BuiltIns.do_tell(self, args)
        elif (name == 'crypt'):
            BuiltIns.do_crypt(self, args)
        elif (name == 'chop'):
            BuiltIns.do_chop(self, args)
        elif (name == 'sleep'):
            BuiltIns.do_sleep(self, args)
        elif (name == 'push'):
            BuiltIns.do_push(self, args)
        elif (name == 'pop'):
            BuiltIns.do_pop(self, args)
        elif (name == 'split'):
            BuiltIns.do_split(self, args)
        elif (name == 'ord'):
            BuiltIns.do_ord(self, args)
        elif (name == 'chr'):
            BuiltIns.do_chr(self, args)
        elif (name == 'hex'):
            BuiltIns.do_hex(self, args)
        elif (name == 'oct'):
            BuiltIns.do_oct(self, args)
        elif (name == 'int'):
            BuiltIns.do_int(self, args)
        elif (name == 'time'):
            BuiltIns.do_time(self, args)
        elif (name == 'gmtime'):
            BuiltIns.do_gmtime(self, args)
        elif (name == 'localtime'):
            BuiltIns.do_localtime(self, args)
        elif (name == 'stat'):
            BuiltIns.do_stat(self, args)
        elif (name == 'substr'):
            BuiltIns.do_substr(self, args)
        elif (name == 'exp'):
            BuiltIns.do_exp(self, args)
        elif (name == 'log'):
            BuiltIns.do_log(self, args)
        elif (name == 'sqrt'):
            BuiltIns.do_sqrt(self, args)
        elif (name == 'chdir'):
            BuiltIns.do_chdir(self, args)
        elif (name == 'umask'):
            BuiltIns.do_umask(self, args)
        elif (name == 'rename'):
            BuiltIns.do_rename(self, args)
        elif (name == 'unlink'):
            BuiltIns.do_unlink(self, args)
        elif (name == 'link'):
            BuiltIns.do_link(self, args)
        elif (name == 'chmod'):
            BuiltIns.do_chmod(self, args)
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
        if (index_expr == True):
            val = self.stack.pop()
            idx = self.stack.pop()
            if (type(idx._val) is str):
                v = self.get_variable(name, 'hash')
                v[idx.stringify()] = val.scalar_context()
                self.set_variable(name, v, 'hash')
            else:
                v = self.get_variable(name, 'list')
                v[idx.numerify()] = val.scalar_context()
                self.set_variable(name, v, 'list')
         
            # push the assigned val back to the stack
            self.stack.push(v)
        else:
            v = self.get_variable(name, 'scalar')
            v = self.stack.pop().scalar_context()
            self.set_variable(name, v, 'scalar')
            
            # push the assigned val back to the stack
            self.stack.push(v)

    def perform_push_anon_list(self, length):
        arry = Value([])
        for i in range(0, length):
            arry.push(self.stack.pop())
        arry.reverse()
        self.stack.push(arry)
        
    def perform_multi_assign(self, var_list, elem_count):
        vals = []
        if elem_count == 1 and self.stack[-1].type == 'List':
            # we'll need to check if the top of stack 
            # is a list, if so we'll need to break it apart
            # and use its length for 'elem_count'
            elem_count = len(self.stack[-1]._val)
            vals = self.stack.pop()
        else:
            for i in range(0, elem_count):
                vals.append(self.stack.pop())

        first_val = Value(None)
        for var in range(0, len(var_list)):
            if elem_count > 0:
                if var_list[var][0] == '$':
                    new_val = vals[var] if (type(vals[var]) is Value) else Value(vals[var])
                    self.set_variable(var_list[var][1:], new_val, 'scalar')
                    if var == 0: 
                        first_val = self.get_variable(var_list[var][1:], 'scalar')
                    elem_count -= 1
                elif var_list[var][0] == '@':
                    # if we hit the '@' list context, take rest of rval
                    new_val = vals[var:] if (type(vals[var:]) is Value) else Value(vals[var:])
                    self.set_variable(var_list[var][1:], new_val, 'list')
                    if var == 0: 
                        first_val = self.get_variable(var_list[var][1:], 'list')
                    elem_count = 0  # any more assignments to var_list will be undefs
            else:
                if var_list[var][0] == '$':
                    self.set_variable(var_list[var][1:], Value(None), 'scalar')
                elif var_list[var][0] == '@':
                    self.set_variable(var_list[var][1:], Value(None), 'list')
        
        # push the first of the assigned vals back on stack 
        self.stack.push(first_val)        
                
    def perform_list_assign(self, name, length):
        arry = Value([])
        for i in range(0, length):
            stack_val = self.stack.pop()
            if stack_val.type == 'List':
                temp = []
                for j in stack_val._val:
                    temp.append(Value(j))  
                temp.reverse()
                for i in temp:
                    arry.push(i)
            else:
                arry.push(stack_val)

        arry.reverse()
        self.set_variable(name, arry, 'list')
        
    def die(self):
        sys.exit(1)

