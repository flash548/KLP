from Lexer import *
from Parser import *
from AST import *
from VM import *

print "\n------- NEW RUN -------\n"

fp = open('t/op.eval')
code = fp.read()
fp.close()

# l = Lexer(code)
l = Lexer(""" 
$@ = "hello";
print $@;
#if ($@ eq "") { print "SDF"; }
""")

#l.dump_tokens()
#exit(1);
p = Parser(l)
ast = p.program()
v = VM()
ast.emit(v)
v.dump_pgm_stack()
v.run()

print "\n\n"
v.dump_current_scope()
v.dump_stack()
