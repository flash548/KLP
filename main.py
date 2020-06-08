#! /usr/bin/python -B

from Lexer import *
from Parser import *
from AST import *
from VM import *
import sys, os, re

s = None

# init the lexer and vm objs as globals
# lexer gets init'd later on
lex = None
vm = VM()

try:
    global _stash
    s = _stash
    vm.is_stash = True
    vm._stash = s
except:
    pass

# set the %ENV hash in the VM
env = vm.get_variable('ENV', 'hash')
env._val = os.environ
vm.set_variable('ENV', env, 'hash')

# set $$
vm.set_variable('$', Value(os.getpid()), 'scalar')

# set the value of stdin, stdout, stderr within the VM
vm.set_variable('stdin', Value(sys.stdin), 'raw')
vm.set_variable('stdout', Value(sys.stdout), 'raw')
vm.set_variable('stderr', Value(sys.stderr), 'raw')

# Note len sys.argv will always be at least 1! (main.py)

is_stdin = False
is_n = False
is_e = False
is_dump = False
is_dump_toks = False
code = ''
filename = ''
arg_count = 0
argv_list = []
for arg in sys.argv[1:]:

    if is_e and code == '':
        code = arg
    elif (is_e or filename != '') and (not arg.startswith('-') or len(arg) == 1):
        # take rest as ARGV
        argv_list.append(arg)
    else:
        if (arg == '-'):
            is_stdin = True
            break
        elif (arg.startswith('-')):
            idx = 1
            for sw in arg[1:]:
                if sw == 'n':
                    is_n = True
                elif sw == 'd':
                    is_dump = True
                elif sw == 'D':
                    is_dump_toks = True
                elif sw == 'e':
                    is_e = True
                    if len(arg[idx:])-1 == idx: # end of arg, jump to next for contents
                        continue
                    else:
                        code = arg[idx+1:]
                        break

                idx += 1
        else:
            # must be a filename
            filename = arg

    arg_count += 1


else:
    if (len(sys.argv) <= 1 or is_stdin):
        vm.set_variable('ARGV', Value([]), 'list')
        # set the perl $0 to <stdin>
        vm.set_variable('0', Value('-'), 'scalar')
        code = sys.stdin.read()
    elif (filename != ''):
        # set the perl $0 to name of the script
        vm.set_variable('0', Value(filename), 'scalar')
        vm.set_variable('ARGV', Value(argv_list), 'list')
        fp = open(filename)
        code = fp.read()
        fp.close()
    else:
        # run the -e code
        vm.set_variable('ARGV', Value(argv_list), 'list')
        # set the perl $0 to <stdin>
        vm.set_variable('0', Value('-'), 'scalar')

if is_n:
    code = "while (<>) { " + code + "}"

lex = Lexer(code)
if (is_dump_toks):
    # dump tokens and exit
    lex.dump_tokens()
    sys.exit(0)

# scan, parse, to IR (AST)
p = Parser(lex)
ast = p.parse()

# walk and emit bytecode from AST (compile)
ast.emit(vm)

# run the VM
#try:
if (not is_dump):
    vm.run()
else:
    vm.dump_pgm_stack()
#except Exception as e:
#    print str(e)
    #pass

#vm.dump_current_scope()
#v.dump_stack()
