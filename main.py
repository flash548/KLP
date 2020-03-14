from Lexer import *
from Parser import *
from AST import *
from VM import *

l = Lexer("""
    @a = (2,2,3); 
    $a[4]=87; 
    $b = 4;
    $c = "Chris";
    print(0+@a);
    print($b);
    print($c);
    if (1  & 0) {
        print("hello");
    }
    elsif (1 & 2) { print("yep"); }
    elsif (1 & 1) { print("yep2"); }
    else { 
        print("nope"); 
    }
    print "here";
    $i = 0;
    while ($i < 5) {
        print($i);
        $i = $i + 1;
    }
    """)
p = Parser(l)
ast = p.program()
v = VM()
ast.emit(v)
v.dump_pgm_stack()
v.run()


#v.dump_current_scope()