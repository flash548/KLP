from Lexer import *
from Parser import *
from AST import *
from VM import *

print "\n------- NEW RUN -------\n"
# TODO:
# short circuit ops
# 'or' 'and' 'xor' operators and precedence (but perl 1-4 didn't have these)
# functions (declarations and do blocks)
# matching/substr
# hashes
# require statement (but perl 1 didn't have)
# scopes (but perl 1 didn't have)
# magic variables

# l = Lexer("""
    # @a = (2,2,3); 
    # $a[4]=87; 
    # $b = 4;
    # $c = "Chris";
    # print(0+@a);
    # print($b);
    # print($c);
    # if (1  & 0) {
        # print("hello");
    # }
    # elsif (1 & 2) { print("yep"); }
    # elsif (1 & 1) { print("yep2"); }
    # else { 
        # print("nope"); 
    # }
    # print "here";
    # $i = 0;
    # while ($i < 5) {
        # print($i);
        # last if ($i == 2);
        # $i = $i + 1;
    # }
    # until (1) {
        # print "here uness";
    # }
    # print "yoyo" unless 0;
    # """)
    
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
print join(' ',@x);

""")

p = Parser(l)
ast = p.program()
v = VM()
ast.emit(v)
#v.dump_pgm_stack()
v.run()

print "\n\n"
#v.dump_current_scope()
#v.dump_pgm_stack('test')
#v.dump_stack()
