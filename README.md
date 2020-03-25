Perl on Python for Pythonista (3P) is an attempt to implement very basic functionality of core Perl using Python 2.7.  The target is Pythonista on iOS - I was thinking mainly for use on StaSh for Pythonista.  I wanted Perl to be able to do some basic text analysis and processing.  Yes you can use Python to do that, but I'm used to Perl and thought this might be a fun project (maybe).  The level of functionality here would be akin to something of Perl 1.0 at this point ...and its a slow work in progress.  

This is also another attempt to learn to write a full blown lexer/parser/compiler.  There's a great tutorial out there - https://ruslanspivak.com/lsbasi-part1/ that got me started on this and other language writing projects. 

I apologize for lack of documentation at this point, but I'll be documenting more in the near future.

Basic overview-
Lexer.py - The lexer/scanner class which produces tokens for the Parser

Parser.py - Parses the language grammar by consuming (expected) tokens, and produces an Abstract Syntax Tree

AST.py - Custom AST with all the various subclasses representing various contructs of the language.  By 'walking' the tree, we call on each class' emit() method to emit its bytecodes and arguments into an instance of the virtual machine.

VM.py - Virtual Machine.  Executes bytecodes and manages the expression stack and symbol/variable table(s).  At this point everything's global and there's no scopes - in the full spirit of Perl 1.

TokenType.py - Defines all the tokens we're working with

main.py - A simple driver app to run some language statements

Value.py - Everything we parse is a 'value'...everything on the stack is a 'value. A Value is any object, but can be interpreted differently depending on the context - just like Perl's values.
