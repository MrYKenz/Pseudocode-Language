from rply import ParserGenerator, Token
from lexer import token_names, lex
import ast
from typing import Union

pg = ParserGenerator(
    token_names,
    precedence=[
        ("left", ["ADD", "MINUS"]),
        ("left", ["MULTIPLY", "DIVIDE"]),
    ]
)


# Program structure
@pg.production('pgm : head decpart bodypart tail')
def program(p):
    head, decpart, bodypart, tail = p
    assert head.getstr() == tail.getstr()
    return ast.Program(head.getstr(), decpart, bodypart)


@pg.production('head : PROGRAM ID')
def head(p):
    return p[1]


@pg.production('decpart : declist')
def declare(p):
    return p[0]


@pg.production('bodypart : SUBROUTINE ID PAREN_L PAREN_R stmtlst ENDSUBROUTINE')
def bodypart(p):
    return p[4]


@pg.production('tail : END ID')
def tail(p):
    return p[1]


# Declarations
@pg.production('declist : INTEGER varlst')
def declist_int(p):
    return p[1]


@pg.production('declist : declist INTEGER varlst')
def declist_list(p):
    return p[0].extend(p[2])


@pg.production('varlst : varlst COMMA ID')
def varlst_varlst(p):
    return p[0].append_id_token(p[2])


@pg.production('varlst : ID')
def varlst_id(p):
    return ast.IdentifierList.from_id_token(p[0])


# Body
@pg.production('stmtlst : stmt')
def stmtlist_stmt(p):
    return ast.Block.from_statement(p[0])


@pg.production('stmtlst : stmtlst stmt')
def stmtlist_stmtlist(p):
    return p[0].append(p[1])


@pg.production('stmt : OUTPUT exp')
def output_statement(p):
    return ast.OutputStatement(p[1])


@pg.production('stmt : ID ASSIGN exp')
def assign(p):
    assert p[0].gettokentype() == "ID"
    return ast.Assignment(ast.IdentifierReference(p[0].getstr()), p[2])


# Expression evaluation
@pg.production('exp : exp PLUS exp')
@pg.production('exp : exp MINUS exp')
@pg.production('exp : exp MULTIPLY exp')
@pg.production('exp : exp DIVIDE exp')
def exp_binary_term(p):
    token_type, left, right = p[1].gettokentype(), p[0], p[2]
    mapping = {
        "PLUS": ast.Add,
        "MINUS": ast.Subtract,
        "MULTIPLY": ast.Multiply,
        "DIVIDE": ast.Divide,
    }
    return mapping[token_type](left, right)


@pg.production('exp : NUM')
def factor_num(p):
    return ast.Number(int(p[0].getstr()))


@pg.production('exp : MINUS NUM')
def factor_negative_num(p):
    return ast.Number(-int(p[1].getstr()))


@pg.production('exp : ID')
def factor_id(p):
    return ast.IdentifierReference(p[0].getstr())


@pg.production('exp : PAREN_L exp PAREN_R')
def factor_parens(p):
    return p[1]


parser = pg.build()

if __name__ == "__main__":
    from sys import argv
    with open(argv[1], "r") as f:
        p = parser.parse(lex(f.read()))
    print(p.__dict__)
    print(p.eval({}))
