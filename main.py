from Lexer import *
from Parser import *
from AST import *
from VM import *

print "\n------- NEW RUN -------\n"

fp = open('t/op.subst')
code = fp.read()
fp.close()

#l = Lexer(code)
l = Lexer(""" 
$_ = "x";
print "\$x $x";
s/x/\$x $x/;
print "#3\t:$_: eq :\$x foo:\n";
if ($_ eq '$x foo') {print "ok 3\n";} else {print "not ok 3\n";}
""")


p = Parser(l)
ast = p.program()
v = VM()
ast.emit(v)
v.dump_pgm_stack()
v.run()

print "\n\n"
v.dump_current_scope()
v.dump_stack()
