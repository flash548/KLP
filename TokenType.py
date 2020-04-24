class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        return str(self.type) + ": " + str(self.value)


class TokenType:
    INTEGER = "INTEGER"
    FLOAT = "FLOAT"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    POW = "POW"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    BOOL = "BOOL"
    NOT = "NOT"
    EOF = "EOF"
    AND = "AND"
    LOGAND = "LOGICAL AND"
    LOGOR = "LOGICAL OR"
    OR = "OR"
    XOR = "XOR"
    MOD = "MOD"
    GT = "GT"
    LT = "LT"
    GTE = "GTE"
    LTE = "LTE"
    NEQ = "NEQ"
    ASSIGN = "ASSIGN"
    EQ = "EQ"
    STR = "STR"
    INTERP_STR = "INTERP_STR"
    STR_CONCAT = "STR_CONCAT"
    LSHIFT = "LSHIFT"
    RSHIFT = "RSHIFT"
    COLON = "COLON"
    ID = "ID"
    NEWLINE = "NEWLINE"
    FUNC_CALL = "FUNC_CALL"
    IF = "IF"
    ELSE = "ELSE"
    ELSIF = "ELSIF"
    THEN = "THEN"
    COMMA = "COMMA"
    WHILE = "WHILE"
    PLUSPLUS = "PLUSPLUS"
    MINUSMINUS = "MINUSMINUS"
    INCR = "INCR"
    DECR = "DECR"
    COMMENT = "COMMENT"
    FUNCTION_DECLARE = "FUNCTION_DECLARE"
    END_FUNCTION = "END_FUNCTION"
    RETURN = "RETURN"
    FOR = "FOR"
    NEXT = "NEXT"
    LAST = "LAST"
    CONTINUE = "CONTINUE"
    UNTIL = "UNTIL"
    UNLESS = "UNLESS"
    STEP = "STEP"
    TO = "TO"
    SEMICOLON = "SEMICOLON"
    INFINITY = "INFINITY"
    NEG_INFINITY = "-INFINITY"
    LCURLY = "LCURLY"
    RCURLY = "RCURLY"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    STR_EQ = "STR_EQ"
    STR_NEQ = "STR_NEQ"
    STR_LE = "STR_LE"
    STR_LT = "STR_LT"
    STR_GE = "STR_GE"
    STR_GT = "STR_GT"
    MATCH = "MATCH"
    NOT_MATCH = "NOT MATCH"
    COLONCOLON = "COLONCOLON"
    DOTDOT = "DOTDOT"
    DO = "DO"
    BACKTICK = 'BACKTICK'
    COMPLEMENT = 'COMPLEMENT'
    SCALAR = 'SCALAR'
    LIST = 'LIST'
    HASH = 'HASH'
    LIST_MAX_INDEX = 'LIST_MAX_INDEX'
    END_OF_SOURCE = "END OF SOURCE"
    MATCH_SPEC = "MATCH_SPEC"
    TRANS_SPEC = "TRANS_SPEC"
    SUBS_SPEC = "SUBS_SPEC"
    
    BUILTINS = [ 
        'print',
        'length',
        'join',
        'keys',
        'values',
        'each'
    ]
