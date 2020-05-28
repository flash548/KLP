from Lexer import *
from Parser import *
from AST import *
from VM import *
import sys
import fileinput

l = None
v = VM()

v.set_variable('0', Value(__file__), 'scalar')

if len(sys.argv[2:]) > 0:
    # input args specified, save them to @ARGV
    v.set_variable('ARGV', Value(sys.argv[2:]), 'list')
else:
    # no input args specified
    v.set_variable('ARGV', Value([]), 'list')

v.set_variable('stdin', Value(sys.stdin), 'raw')


if len(sys.argv) >= 2:
    fp = open(sys.argv[1])
    code = fp.read()
    fp.close()
    l = Lexer(code)
else:
    code = sys.stdin.read()
    l = Lexer(code)

p = Parser(l)
ast = p.program()

ast.emit(v)
v.dump_pgm_stack()
try:
    v.run()
except:
    pass

v.dump_current_scope()
#v.dump_stack()
