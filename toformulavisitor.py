from collections import defaultdict
import ast
import copy
from pysmt.shortcuts import (
    Symbol,
    And,
    GE,
    LT,
    Plus,
    Equals,
    Int,
    TRUE,
    FALSE,
    get_model,
)
from pysmt.typing import INT


class ToFormulaVisitor(ast.NodeVisitor):
    def __init__(self, ssamap):
        if not ssamap:
            ssamap = defaultdict(lambda: 0)
        self.ssamap = ssamap
        self.newssamap = copy.copy(ssamap)
        self.lstack = list()
        self.rstack = list()

    # def visit_Assign(self,node):
    #    ast.NodeVisitor.generic_visit(self, node)
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.lstack.append(self.getNewValueOf(node.id))
        elif isinstance(node.ctx, ast.Load):
            varname = node.id
            self.rstack.append(self.getValueOf(varname))

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        rightResult = self.rstack.pop()
        leftResult = self.rstack.pop()
        # generic mapping based on names, works ~90% of all cases, for the rest we have self._mapName:
        operatorMethodName = "__%s__" % self._mapName(type(node.op).__name__.lower())
        method = getattr(leftResult, operatorMethodName)
        self.rstack.append(method(rightResult))

    def visit_Num(self, node):
        self.rstack.append(Int(node.n))  # ?

    def visit_NameConstant(self, node):
        self.rstack.append(TRUE() if node.value == True else FALSE())  # ?

    def visit_Compare(self, node):  # TODO: unify with BinOp -> remove code duplication
        self.visit(node.left)
        leftResult = self.rstack.pop()
        compResults = list()
        for comparator in node.comparators:
            self.visit(comparator)
            compResults.append(self.rstack.pop())
        assert len(compResults) == 1
        assert len(node.ops) == 1
        op = node.ops[0]
        operatorMethodName = "__%s__" % self._mapName(type(op).__name__.lower())
        print(operatorMethodName)
        method = getattr(leftResult, operatorMethodName)
        self.rstack.append(method(compResults[0]))

    def _mapName(self, methodName):
        return "mul" if methodName == "mult" else methodName

    def getValueOf(self, varname):
        return Symbol("%s@%d" % (varname, self.ssamap[varname]), INT)

    def getNewValueOf(self, varname):
        self.newssamap[varname] += 1
        return Symbol("%s@%d" % (varname, self.newssamap[varname]), INT)

    # def update(self, othervaluation):
    #     for lhs, rhs in zip(self.lstack, self.rstack):
    #         if rhs == Value.getTop():
    #             othervaluation.pop(lhs, None)
    #         else:
    #             othervaluation[lhs] = rhs.actual


program = """
def mybody(x,y):
  while True:
    if x>0:
      x+=1
    else:
      y = (y + 1)*2
    if y>0:
      y-=10
    else:
      x-=100
"""

tree = ast.parse(program)
tree2 = ast.parse('x = 10 + y * 5')

tfv = ToFormulaVisitor(None)
tfv.visit(tree2)
print(tfv.lstack)
print(tfv.rstack)
