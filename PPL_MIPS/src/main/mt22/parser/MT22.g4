//2010013
grammar MT22;

@lexer::header {
from lexererr import *
}

options{
	language=Python3;
}

program: decl_list EOF;

decl_list: decl decl_list | decl;

decl: var_decl | func_decl;

var_decl: id_list COLON var_type SEMI | full_var_decl SEMI;
full_var_decl: ID COMMA full_var_decl COMMA expr | ID COLON var_type ASS expr;

func_decl: ID COLON FUNCTION func_ret_type param_list (INHERIT ID)? block_stmt;

param_decl: INHERIT? OUT? ID COLON para_type;
id_list: ID COMMA id_list | ID;
param_list: LR param_list_body RR;
param_list_body: param_prime | ;
param_prime: param_decl COMMA param_prime | param_decl;




stmt: match_stmt | unmatch_stmt;
match_stmt: IF sub_expr match_stmt ELSE match_stmt
               | assign_stmt | call_stmt
               | return_stmt
               | for_stmt | while_stmt
               | do_while_stmt | block_stmt
               | continue_stmt | break_stmt;
unmatch_stmt: IF sub_expr stmt
              | IF sub_expr match_stmt ELSE unmatch_stmt;


stov: var_decl | stmt;
stov_list: stov stov_list | ;
//STATEMENT SYNTAX
assign_stmt: lhs ASS expr SEMI;


for_stmt: FOR LR lhs ASS expr COMMA expr COMMA expr RR stmt;

while_stmt: WHILE LR expr RR stmt;
do_while_stmt: DO stmt WHILE LR expr RR SEMI;
block_stmt: LC stov_list RC;
call_stmt: ID LR expr_list RR SEMI;
break_stmt: BREAK SEMI;
continue_stmt: CONTINUE SEMI;
return_stmt: RETURN (expr)? SEMI;

expr: expr0;
expr_list: exprprime | ;
exprprime: expr COMMA exprprime | expr;

//OPERATOR PRECEDENCE AND ASSOCIATION
expr0: expr1 STR_OPR expr1 | expr1;
expr1: expr2 (EQ | NEQ | LT | GT | LTE | GTE) expr2 | expr2;
expr2: expr2 (AND | OR) expr3 | expr3;
expr3: expr3 (ADD | MINUS) expr4 | expr4;
expr4: expr4 (MUL | DIV | MOD) expr5 | expr5;
expr5: NOT expr5 | expr6;
expr6: MINUS expr6 | expr7;

expr7: ID | constant | func_call_expr | sub_expr | index_expr;

func_call_expr: ID LR expr_list RR;
constant: STRINGLIT | BOOLEANLIT | INTLIT | FLOATLIT | array_lit;
sub_expr: LR expr RR;
index_operator: LS exprprime RS;
array_lit: LC expr_list RC;

var_type: atomic_type | array_type | auto_type;
func_ret_type: var_type | void_type;
para_type: atomic_type | array_type;
//para_type: var_type;
atomic_type: INTEGER | FLOAT | STRING | BOOLEAN;
array_type: ARRAY dimension OF atomic_type;
dimension: LS intlit_list RS;

void_type: VOID;
auto_type: AUTO;
intlit_list: INTLIT COMMA intlit_list | INTLIT;
lhs: ID | index_expr;
index_expr: ID index_operator;


//LITERAL:

BOOLEANLIT: TRUE | FALSE;

FLOATLIT: (INTPART DECPART | INTPART EXPPART | '.' DIGIT_SEQ EXPPART| INTPART DECPART EXPPART)
    {self.text = self.text.replace('_', '')};

INTLIT: INTPART
    {self.text = self.text.replace('_', '')};
fragment DECPART: '.' DIGIT_SEQ?;
fragment EXPPART: [eE] [-+]? DIGIT_SEQ;
fragment DIGIT_SEQ: [0-9][0-9]*;


fragment INTPART: '0' | [1-9] [0-9]* ('_'[0-9]+)* ;


STRINGLIT: ["] STRINGABLE_CHARACTER* ["] {self.text = self.text[1:-1]};
fragment STRINGABLE_CHARACTER: ~[\n"\\'] | STRINGABLE_ESCAPE;
//do not contain \n or EOF
fragment STRINGABLE_ESCAPE: '\\' [bfrnt"'\\];
fragment ILLEGAL_ESCAPE_CHARACTER: '\\' ~[btnfr"'\\];


//KEY_WORD
INTEGER: 'integer';
FLOAT: 'float';
RETURN: 'return';
AUTO: 'auto';
BREAK: 'break';
FALSE: 'false';
VOID: 'void';
ARRAY: 'array';
OUT: 'out';
BOOLEAN: 'boolean';
FOR: 'for';
STRING: 'string';
CONTINUE: 'continue';
DO: 'do';
FUNCTION: 'function';
TRUE: 'true';
OF: 'of';
INHERIT: 'inherit';
ELSE: 'else';
IF: 'if';
WHILE: 'while';

//COMMENT
CPP_STYLE_CMT: '//' ~[\r\n]* -> skip;
C_STYLE_CMT: '/*' .*? '*/' -> skip;



//SEPERATORS
SEMI: ';';
COMMA: ',';
COLON: ':';
LR: '(';
RR: ')';
LC: '{';
RC: '}';
LS: '[';
RS: ']';


//OPERATOR
ASS: '=';
MUL: '*';
DIV: '/';
ADD: '+';
MINUS: '-';
NOT: '!';
LTE: '<=';
GTE: '>=';
NEQ: '!=';
EQ: '==';
LT : '<' ;
GT : '>' ;
STR_OPR: '::';
AND: '&&';
OR: '||';
MOD: '%';


ID: [a-zA-Z_] [0-9a-zA-Z_]*;

WS : [ \f\b\t\r\n]+ -> skip ; // skip spaces, tabs, newlines


UNCLOSE_STRING: '"' STRINGABLE_CHARACTER* (EOF  | [\r\n]) {
        raise UncloseString(self.text[1:].replace('\n','').replace('\r',''))
};

ILLEGAL_ESCAPE: ["] STRINGABLE_CHARACTER* ILLEGAL_ESCAPE_CHARACTER {
		raise IllegalEscape(self.text[1:])
};

ERROR_CHAR: . {
		raise ErrorToken(self.text)
};