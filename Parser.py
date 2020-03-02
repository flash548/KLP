from AST import *

class Parser:
	def __init__(self, lexer):
		self.lineNumber = 1
		self.lex = lexer
		self.current_token = lex.getNextToken()
		
	def error(self):
		raise Exception("Invalid syntax on line: " + str(lineNumber))
		
	def parse(self):
		return expr()
		
	def eat(self, tokType):
		if self.current_token.type == tokType:
			if tokType == TokenType.NEWLINE: self.lineNumber += 1
			self.current_token = self.lex.getNextToken()
		else:
			error()
	
	def eat_end_of_statement(self):
		if self.current_token.type == TokenType.SEMICOLON:
			eat(TokenType.SEMICOLON)
	
	def program(self):
		return RootNode(self.statement_list())
		
	def statement_list(self):
		nodes = []
		node = statement()
		nodes.append(node)
		
		while self.current_token.type != TokenType.EOF:
			self.eat_end_of_statement()
			nodes.append(statement())
			
		if self.current_token.type == TokenType.ID:
			error()
			
		return nodes
		
	def statement(self):
		if self.current_token.type == TokenType.CONTEXT:
			return self.assignment_statement()
		elif self.current_token.type == TokenType.IF:
			return self.if_statement()
		elif self.current_token.type == TokenType.WHILE:
			return self.while_statement()
		elif self.current_token.type == TokenType.FUNCTION_DECLARE:
			return function_declare_statement()
		else:
			return ASTNode()
			
		raise Exception("Invalid statement, line number: " + str(self.lineNumber))
		
	
