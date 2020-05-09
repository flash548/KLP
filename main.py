from Lexer import *
from Parser import *
from AST import *
from VM import *

print "\n------- NEW RUN -------\n"


l = Lexer("""

@arr = (1,2,3);
$x= 'abc';
$a=chop $x;
print $a;
print $x;
""")

p = Parser(l)
ast = p.program()
v = VM()
ast.emit(v)
v.dump_pgm_stack()
v.run()

print "\n\n"
v.dump_current_scope()
#v.dump_stack()
