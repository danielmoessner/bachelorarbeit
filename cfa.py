import ast
import astunparse
from enum import Enum


class CFANode:
    index = 0

    def __init__(self):
        self.nodeNumber = CFANode.index
        self.enteringEdges = list()
        self.leavingEdges = list()
        CFANode.index += 1

    def __str__(self):
        return "(%s)" % str(self.nodeNumber)

    @staticmethod
    def merge(a, b):
        mergedNode = CFANode()
        for enteringEdge in b.enteringEdges:
            enteringEdge.successor = a
            a.enteringEdges.append(enteringEdge)
        for (
            leavingEdge
        ) in (
            b.leavingEdges
        ):  # might not be needed even since we merge only sucessorless b-nodes
            leavingEdge.predecessor = a
            a.leavingEdges.append(leavingEdge)
        b.enteringEdges = list()
        b.leavingEdges = list()
        if CFANode.index == b.nodeNumber + 1:
            CFANode.index -= 1
        return a


class InstructionType(Enum):
    STATEMENT = 1
    ASSUMPTION = 2


class Instruction:
    """An instruction is either an assignment or an assumption"""

    def __init__(self, expression, kind=InstructionType.STATEMENT, negated=False):
        self.kind = kind
        self.expression = expression
        self.negated = negated  # we might need this information at some point

    @staticmethod
    def assumption(expression, negated=False):
        if negated:
            expression = ast.UnaryOp(op=ast.Not(), operand=expression)
        return Instruction(expression, kind=InstructionType.ASSUMPTION, negated=negated)

    @staticmethod
    def statement(expression):
        return Instruction(expression)


class CFAEdge:
    def __init__(self, predecessor, successor, instruction):
        self.predecessor = predecessor
        self.successor = successor
        predecessor.leavingEdges.append(self)
        successor.enteringEdges.append(self)
        self.instruction = instruction

    def __str__(self):
        return "%s -%s-> %s" % (
            str(self.predecessor),
            self.label(),
            str(self.successor),
        )

    def label(self):
        return astunparse.unparse(self.instruction.expression).strip()


class CFACreator(ast.NodeVisitor):
    def __init__(self):
        self.root = CFANode()
        self.nodestack = list()
        self.nodestack.append(self.root)

    def visit_FunctionDef(self, node):
        ast.NodeVisitor.generic_visit(self, node)

    def visit_While(self, node):
        entrynode = self.nodestack.pop()
        inside = CFANode()
        edge = CFAEdge(entrynode, inside, Instruction.assumption(node.test))
        outside = CFANode()
        edge = CFAEdge(
            entrynode, outside, Instruction.assumption(node.test, negated=True)
        )
        self.nodestack.append(inside)
        for statement in node.body:
            self.visit(statement)
        bodyexitnode = self.nodestack.pop()
        CFANode.merge(entrynode, bodyexitnode)
        self.nodestack.append(outside)

    def visit_If(self, node):
        entrynode = self.nodestack.pop()
        left = CFANode()
        edge = CFAEdge(entrynode, left, Instruction.assumption(node.test))
        right = CFANode()
        edge = CFAEdge(
            entrynode, right, Instruction.assumption(node.test, negated=True)
        )
        self.nodestack.append(left)
        for statement in node.body:
            self.visit(statement)
        leftexit = self.nodestack.pop()
        self.nodestack.append(right)
        for statement in node.orelse:
            self.visit(statement)
        rightexit = self.nodestack.pop()
        mergedExit = CFANode.merge(leftexit, rightexit)
        self.nodestack.append(mergedExit)

    def visit_Expr(self, node):
        entrynode = self.nodestack.pop()
        exitNode = CFANode()
        edge = CFAEdge(entrynode, exitNode, Instruction.statement(node.value))
        self.nodestack.append(exitNode)

    def visit_AugAssign(self, node):
        self.visit_Assign(node)

    def visit_Assign(self, node):
        entryNode = self.nodestack.pop()
        exitNode = CFANode()
        edge = CFAEdge(entryNode, exitNode, Instruction.statement(node))
        self.nodestack.append(exitNode)
