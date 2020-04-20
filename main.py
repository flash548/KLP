from Lexer import *
from Parser import *
from AST import *
from VM import *

print "\n------- NEW RUN -------\n"

l = Lexer("""
print "1..6\n";

print "ok 1\n" if 1;
print "not ok 1\n" unless 1;

print "ok 2\n" unless 0;
print "not ok 2\n" if 0;

1 && (print "not ok 3\n") if 0;
1 && (print "ok 3\n") if 1;
0 || (print "not ok 4\n") if 0;
0 || (print "ok 4\n") if 1;

$x = 0;
do {$x[$x] = $x;} while ($x++) < 10;
if (join(' ',@x) eq '0 1 2 3 4 5 6 7 8 9 10') {
	print "ok 5\n";
} else {
	print "not ok 5\n";
}

$x = 15;
$x = 10 while $x < 10;
if ($x == 15) {print "ok 6\n";} else {print "not ok 6\n";}
""")

p = Parser(l)
ast = p.program()
v = VM()
ast.emit(v)
v.dump_pgm_stack()
v.dump_pgm_stack('foo')
v.run()

print "\n\n"
v.dump_current_scope()
#v.dump_pgm_stack('test')
v.dump_stack()
