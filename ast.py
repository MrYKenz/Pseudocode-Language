from __future__ import division

from rply.token import BaseBox, Token 
from typing import Optional, Iterator
import os


class ASTNode(BaseBox):
    def eval(self, context):
        raise NotImplementedError(self.__class__)


class IdentifierList(BaseBox):
    def __init__(self, identifiers):
        self.identifiers = identifiers

    @staticmethod
    def from_id_token(tok):
        id = Identifier(tok.getstr())
        return IdentifierList([id])

    def append_id_token(self, tok):
        id = Identifier(tok.getstr())
        self.identifiers.append(id)
        return self

    def extend(self, other):
        assert isinstance(other, IdentifierList)
        self.identifiers.extend(other.identifiers)
        return self

    def __iter__(self):
        return iter(self.identifiers)


class Block(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    @staticmethod
    def from_statement(statement):
        return Block([statement])

    def extend(self, other):
        assert isinstance(other, Block)
        self.statements.extend(other.statements)
        return self

    def append(self, statement):
        self.statements.append(statement)
        return self

    def eval(self, context):
        for statement in self.statements:
            statement.eval(context)


class Number(ASTNode):
    def __init__(self, value):
        self.intvalue = value

    def getint(self):
        return self.intvalue

    def eval(self, context):
        return self


class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name


class IdentifierReference(ASTNode):
    def __init__(self, name):
        self.name = name

    def eval(self, context):
        return context[self.name]


class Program(ASTNode):
    def __init__(self, name, decls, body):
        self.name = name
        self.variables = decls
        self.subroutine = body

    def eval(self, context):
        for identifier in self.variables:
            context[identifier.name] = Number(0)
        self.subroutine.eval(context)


class BinaryOperation(ASTNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def value_of(self, node, context):
        v = node.eval(context)
        if v is None or not isinstance(v, Number):
            raise AssertionError("Expected numeric value: %s" % v)
        return v


class Add(BinaryOperation):
    def eval(self, context):
        return Number(self.value_of(self.left, context).getint() +
                      self.value_of(self.right, context).getint())


class Subtract(BinaryOperation):
    def eval(self, context):
        return Number(self.value_of(self.left, context).getint() -
                      self.value_of(self.right, context).getint())


class Multiply(BinaryOperation):
    def eval(self, context):
        return Number(self.value_of(self.left, context).getint() *
                      self.value_of(self.right, context).getint())


class Divide(BinaryOperation):
    def eval(self, context):
        return Number(self.value_of(self.left, context).getint() //
                      self.value_of(self.right, context).getint())


class Assignment(ASTNode):
    def __init__(self, identifier, value):
        self.identifier = identifier
        self.value = value

    def eval(self, context):
        assert self.identifier.name in context
        value = self.value.eval(context)
        if value is None:
            raise AssertionError("Attempting to assign a null value")
        context[self.identifier.name] = value



class OutputStatement(ASTNode):
    def __init__(self, value, newline=True):
        self.value = value
        self.newline = newline

    @staticmethod
    def int_to_bytes(i):
        try:
            _ = b"a" + "a"
            return str(i)
        except:
            return str(i).encode("ascii")

    def eval(self, context):
        os.write(1, self.int_to_bytes(self.value.eval(context).getint()) +
                 (b"\n" if self.newline else b""))
