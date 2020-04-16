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
#!./perl

# $Header: cmd.subval,v 1.0 87/12/18 13:12:12 root Exp $

sub foo1 {
    'true1';
    if ($_[0]) { 'true2'; }
}

sub foo2 {
    'true1';
    if ($_[0]) { 'true2'; } else { 'true3'; }
}

sub foo3 {
    'true1';
    unless ($_[0]) { 'true2'; }
}

sub foo4 {
    'true1';
    unless ($_[0]) { 'true2'; } else { 'true3'; }
}

sub foo5 {
    'true1';
    'true2' if $_[0];
}

sub foo6 {
    'true1';
    'true2' unless $_[0];
}

print "1..12\n";

if (do foo1(0) eq '0') {print "ok 1\n";} else {print "not ok 1\n";}
if (do foo1(1) eq 'true2') {print "ok 2\n";} else {print "not ok 2\n";}
if (do foo2(0) eq 'true3') {print "ok 3\n";} else {print "not ok 3\n";}
if (do foo2(1) eq 'true2') {print "ok 4\n";} else {print "not ok 4\n";}

if (do foo3(0) eq 'true2') {print "ok 5\n";} else {print "not ok 5\n";}
if (do foo3(1) eq '') {print "ok 6\n";} else {print "not ok 6\n";}
if (do foo4(0) eq 'true2') {print "ok 7\n";} else {print "not ok 7\n";}
if (do foo4(1) eq 'true3') {print "ok 8\n";} else {print "not ok 8\n";}

if (do foo5(0) eq '') {print "ok 9\n";} else {print "not ok 9\n";}
if (do foo5(1) eq 'true2') {print "ok 10\n";} else {print "not ok 10\n";}
if (do foo6(0) eq 'true2') {print "ok 11\n";} else {print "not ok 11\n";}
if (do foo6(1) eq '') {print "ok 12\n";} else {print "not ok 12\n";}

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
