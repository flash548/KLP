from Lexer import *
from Parser import *
from AST import *
from VM import *

print "\n------- NEW RUN -------\n"

l = Lexer("""

@arr=(19,2,3);
@more=(0,1,3);
@indexes=('this','is','an','array');
print $indexes[0];
if ($indexes[0] =~ m/([a-z])/) {
    print "here";
    print $1;
}
$indexes[$more[0]] =~ s/[a-z]/5/;
$arr[1] ^= 1;
$arr[0]++;
print $arr[1];

@a = (1);
for($a[0]=0; $a[0] < 5; $a[0]++) {
    print "hello\n";
}

@strs=("Hello", "Chris");
$strs[1] .= "Zell";
print $strs[1];

$name = "Zell";
$name .= "Chris";
print $name;

print index("Chris", "ris");
print sprintf("%s %i", "franks", 37);

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
