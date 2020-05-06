from Value import Value
import sys
import subprocess
import os

class BuiltIns():

    @staticmethod
    def do_print(vm, fh, argv):
        if (len(argv) > 0):
            if fh == None:
                sys.stdout.write((argv[0]).stringify())
            else:
                vm.get_variable(fh, 'raw')._val.write((argv[0]).stringify())
        else:
            # print $_
            if fh == None:
                sys.stdout.write(vm.get_variable('_', 'scalar').stringify())
            else:
                vm.get_variable(fh, 'raw')._val.write(vm.get_variable('_', 'scalar').stringify())
            
        vm.stack.push(Value(1))
        
    @staticmethod
    def do_die(vm, argv):
        if len(argv) > 0:
            sys.stdout.write((argv[0]).stringify())
        else:
            sys.stdout.write("Died")
            
        vm.die()
        
    @staticmethod
    def do_backticks(vm, cmd):
        result = None
        if os.name == 'nt':
            # windows
            result = subprocess.check_output(['cmd', '/c', cmd.stringify()], stderr=subprocess.STDOUT)
        elif os.name.endswith('ix'):
            # posix-ish - assume bash
            result = subprocess.check_output(['/bin/bash', '-c', cmd.stringify()], stderr=subprocess.STDOUT)
        else:
            Builtins.do_die(vm, "Died.  Unknown OS to do backticks on")

        vm.stack.push(Value(result))
            
    @staticmethod
    def do_length(vm, argv):
        vm.stack.push(Value(len(str(argv[0]))))
        
    @staticmethod
    def do_join(vm, argv):
        ary = argv[0]
        joiner = argv[1]
        tmplist = []            
        for i in range(len(ary)):
            tmplist.append(str(ary[i]))
        
        vm.stack.push(Value(str(joiner).join(tmplist)))
        
    @staticmethod
    def do_keys(vm, argv):
        # perl 1 allows a bareword for hash argument...
        if type(argv[0]) is Value:
            key_arry = argv[0]._val.keys()
            key_arry.reverse()
            vm.stack.push(Value(key_arry))
        else:
            v = vm.get_variable(str(argv[0]), 'hash')
            key_arry = v._val.keys()
            key_arry.reverse()
            vm.stack.push(Value(key_arry))
        
    @staticmethod
    def do_values(vm, argv):
        # perl 1 allows a bareword for hash argument...
        if type(argv[0]) is Value:
            val_arry = argv[0]._val.values()
            val_arry.reverse()
            vm.stack.push(Value(val_arry))
        else:
            v = vm.get_variable(str(argv[0]), 'hash')
            val_arry = v._val.values()
            val_arry.reverse()
            vm.stack.push(Value(val_arry))
        
    @staticmethod
    def do_each(vm, argv):
        # perl 1 allows a bareword for hash argument...
        if type(argv[0]) is Value:
            pair = argv[0]._each()
            vm.stack.push(Value([pair[0], pair[1]]))
        else:
            v = vm.get_variable(str(argv[0]), 'hash')
            pair = v._each()
            vm.stack.push(Value([pair[0], pair[1]]))
        
    @staticmethod
    def do_eval(vm, argv):
        from Lexer import Lexer
        from Parser import Parser
        from VM import VM
        error_msg = ''
        v = None
        try:
            l = Lexer(str(argv[0]))
            p = Parser(l)
            ast = p.program()
            v = VM()
            
            # merge in existing scope, stack, subs, etc
            v.current_scope = vm.current_scope
            v.pgm_stack_frames = vm.pgm_stack_frames
            
            ast.emit(v)
            v.run()
        except Exception as e:
            raise(e)
            error_msg = str(e)
        
        # push the return value back to the main program
        if v != None and len(v.stack) > 0:
            vm.stack.push(v.stack.pop())
        else:
            vm.stack.push(Value(None))
        
        # set $@ result
        vm.set_variable('@', Value(error_msg), 'scalar')
        
    @staticmethod
    def do_open(vm, argv):
        handle = str(argv[1])
        filename = str(argv[0])
        fp = None
        error = ''
        success = True
        try:
            if filename.startswith('>>'):
                fp = open(filename[2:], 'a')
            elif filename.startswith('>'):
                fp = open(filename[1:], 'w')
            elif filename.startswith('<'):
                fp = open(filename[1:], 'r')
            else:
                fp = open(filename, 'r')
        except Exception as e:
            error = str(e)
            success = False
            
        vm.set_variable('!', Value(error), 'scalar')
        vm.set_variable(handle, Value(fp), 'raw')
        vm.last_fh_read = handle
        
        # return success or failure
        vm.stack.push(Value(1) if success else Value(0))
        
    @staticmethod
    def do_close(vm, argv):
        handle = str(argv[0])
        fp = vm.get_variable(handle, 'raw')
        error = ''
        success = True
        try:
            fp._val.close()
        except Exception as e:
            error = str(e)
            success = False
        
        vm.set_variable('!', Value(error), 'scalar')  
        vm.set_variable(handle, Value(fp), 'raw')        
        vm.stack.push(Value(1) if success else Value(0))
        
    @staticmethod
    def do_eof(vm, argv):
        handle = None
        fp = None
        if len(argv) > 0:
            handle = str(argv[0])
            fp = vm.get_variable(handle, 'raw')
        else:
            fp = vm.get_variable(str(vm.last_fh_read), 'raw')
         
        if (fp._val.closed):
            vm.stack.push(Value(1))
            return
            
        pos = fp._val.tell()
        a = fp._val.readline()
        if (a == ''):
            fp._val.seek(pos)
            vm.stack.push(Value(1))
        else:
            fp._val.seek(pos)
            vm.stack.push(Value(0))
    
    @staticmethod
    def do_shift(vm, argv):
        v = vm.get_variable(str(argv[0]), 'list')
        elem0 = Value(None)        
        if (len(v) > 1):
            elem0 = v._val[0]
            vm.set_variable(str(argv[0]), Value(v._val[1:]), 'list')
        elif (len(v) == 1):
            elem0 = v._val[0]
            vm.set_variable(str(argv[0]), Value(None), 'list')
        else:
            vm.set_variable(str(argv[0]), Value(None), 'list')
        vm.stack.push(elem0)

    @staticmethod
    def do_unshift(vm, argv):
        name = str(argv[-1])
        v = vm.get_variable(name, 'list')
        
        for i in range(0, len(argv)-1):
            if (argv[i]._val != None):
                v = v.prepend_list(argv[i])
                vm.set_variable(name, v, 'list')
            
        vm.stack.push(Value(len(v)))
        
    @staticmethod
    def do_index(vm, argv):
        src = str(argv[1])
        search = str(argv[0])
        
        vm.stack.push(Value(src.index(search, 0)))
        
    @staticmethod
    def do_sprintf(vm, argv):
        fmt_str = str(argv[-1])
        strs = []
        for i in range(0, len(argv)-1):
            strs.insert(0, str(i))
            
        vm.stack.push(Value(fmt_str % tuple(strs)))
        