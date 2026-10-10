"""Abstract Syntax Tree (AST) node definitions for the C subset."""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class ASTNode:
    line: int = 1
    column: int = 1
    start_offset: int = 0
    end_offset: int = 0

    def to_dict(self) -> dict[str, Any]:
        result = {"node_type": self.__class__.__name__}
        for k, v in self.__dict__.items():
            if isinstance(v, ASTNode):
                result[k] = v.to_dict()
            elif isinstance(v, list):
                result[k] = [item.to_dict() if isinstance(item, ASTNode) else item for item in v]
            else:
                result[k] = v
        return result


@dataclass
class Program(ASTNode):
    declarations: list[ASTNode] = field(default_factory=list)


@dataclass
class Param(ASTNode):
    type_name: str = ""
    name: str = ""


@dataclass
class FunctionDef(ASTNode):
    return_type: str = ""
    name: str = ""
    params: list[Param] = field(default_factory=list)
    body: Optional["Block"] = None


@dataclass
class Declarator(ASTNode):
    name: str = ""
    init: Optional[ASTNode] = None


@dataclass
class VarDecl(ASTNode):
    type_name: str = ""
    declarators: list[Declarator] = field(default_factory=list)


@dataclass
class Block(ASTNode):
    statements: list[ASTNode] = field(default_factory=list)


@dataclass
class IfStmt(ASTNode):
    condition: Optional[ASTNode] = None
    then_branch: Optional[ASTNode] = None
    else_branch: Optional[ASTNode] = None


@dataclass
class WhileStmt(ASTNode):
    condition: Optional[ASTNode] = None
    body: Optional[ASTNode] = None


@dataclass
class DoWhileStmt(ASTNode):
    body: Optional[ASTNode] = None
    condition: Optional[ASTNode] = None


@dataclass
class ForStmt(ASTNode):
    init: Optional[ASTNode] = None
    condition: Optional[ASTNode] = None
    update: Optional[ASTNode] = None
    body: Optional[ASTNode] = None


@dataclass
class ReturnStmt(ASTNode):
    value: Optional[ASTNode] = None


@dataclass
class BreakStmt(ASTNode):
    pass


@dataclass
class ContinueStmt(ASTNode):
    pass


@dataclass
class ExprStmt(ASTNode):
    expr: Optional[ASTNode] = None


@dataclass
class BinaryExpr(ASTNode):
    left: Optional[ASTNode] = None
    op: str = ""
    right: Optional[ASTNode] = None


@dataclass
class UnaryExpr(ASTNode):
    op: str = ""
    operand: Optional[ASTNode] = None
    prefix: bool = True


@dataclass
class AssignExpr(ASTNode):
    target: Optional[ASTNode] = None
    op: str = "="
    value: Optional[ASTNode] = None


@dataclass
class CallExpr(ASTNode):
    callee: Optional[ASTNode] = None
    args: list[ASTNode] = field(default_factory=list)


@dataclass
class Identifier(ASTNode):
    name: str = ""


@dataclass
class Literal(ASTNode):
    value: Any = None
    raw: str = ""
    literal_type: str = ""


@dataclass
class ArrayAccess(ASTNode):
    array: Optional[ASTNode] = None
    index: Optional[ASTNode] = None


@dataclass
class MemberAccess(ASTNode):
    object: Optional[ASTNode] = None
    member: str = ""
    is_arrow: bool = False
