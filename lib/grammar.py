from lark import Lark
from .s1sast import *

grammar = """
start: q_prop
term : fvar | zero | successor
successor : "S" term 
fvar : ("a".."z")+
svar : ("A".."Z")+
zero : "0"

a_prop: term "=" term -> eq 
        | term "!=" term -> neq
        | term "<" term  -> lt
        | term "<=" term -> le
        | term ">" term -> gt
        | term ">=" term -> ge
        | term "in" svar -> in
        | "!" "("a_prop")" -> not
and: q_prop "&" q_prop -> and
or: q_prop "|" q_prop -> or
impl: a_prop "->" a_prop -> impl
forall: "forall" fvar "." q_prop | "forall" svar "." q_prop
exists: "exists" svar "." q_prop | "exists" fvar "." q_prop
q_prop: forall | exists | a_prop | "!" "("q_prop")" -> not | and | or | impl

%import common.WS
%ignore WS
"""

parser = Lark(grammar)

toy_prog = "exists x.x=y"

def pretty_print(ast, tab_count):
    if hasattr(ast, "children"):
        print("  "*tab_count + ast.data)
        for child in ast.children:
            pretty_print(child, tab_count + 1)
    else: 
        print("  "*tab_count + ast)

def construct_typed_ast(ast):
    match ast.data:
        case 'q_prop':
            return construct_typed_ast(ast.children[0]) #one child
        case 'forall':
            var = construct_typed_ast(ast.children[0])
            expr = construct_typed_ast(ast.children[1])
            return QuantifiedExpr(var,expr, var.get_order(), "forall")
        case 'exists':
            var = construct_typed_ast(ast.children[0])
            expr = construct_typed_ast(ast.children[1])
            return QuantifiedExpr(var,expr, var.get_order(), "exists")
        case 'fvar':
            return FVar(ast.children[0].value.strip())
        case 'svar':
            return SVar(ast.children[0].value.strip())
        case 'eq':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1].children[0])
            return Eq(left,right)
        case 'neq':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1].children[0])
            return Negate(Eq(left,right))
        case 'impl':
            left = construct_typed_ast(ast.children[0])
            right = construct_typed_ast(ast.children[1])
            return Or(Negate(left),right) 
        case 'zero':
            return Zero()
        case 'in':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1])
            return In(left,right)
        case 'lt':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1].children[0])
            return Lt(left,right)
        case 'le':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1].children[0])
            return Or(Lt(left,right), Eq(left,right))
        case 'gt':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1].children[0])
            return Lt(right,left)
        case 'ge':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1].children[0])
            return Negate(Lt(left,right))
        case 'successor':
            return Successor(construct_typed_ast(ast.children[0].children[0]))
        case 'not':
            return Negate(construct_typed_ast(ast.children[0]))
        case 'and':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1].children[0])
            return And(left,right)
        case 'or':
            left = construct_typed_ast(ast.children[0].children[0])
            right = construct_typed_ast(ast.children[1].children[0])
            return Or(left,right)
        case other:
            print("error")
            print(ast)

def extract_vars(tree):
    vars = set()
    if isinstance(tree, QuantifiedExpr):
        vars.add(tree.bound_var.var_name)
        return vars.union(extract_vars(tree.expression))
    elif isinstance(tree, Eq):
        return vars.union(extract_vars(tree.left)).union(extract_vars(tree.right))
    elif isinstance(tree, In):
        return vars.union(extract_vars(tree.left)).union(extract_vars(tree.right))
    elif isinstance(tree, Lt):
        return vars.union(extract_vars(tree.left)).union(extract_vars(tree.right))
    elif isinstance(tree, Negate):
        return vars.union(extract_vars(tree.sub_term))
    elif isinstance(tree, Zero):
        return vars 
    elif isinstance(tree, FVar):
        vars.add(tree.var_name)
        return vars 
    elif isinstance(tree, SVar):
        vars.add(tree.var_name)
        return vars
    elif isinstance(tree, Or):
        return extract_vars(tree.left).union(extract_vars(tree.right))
    elif isinstance(tree, And):
        return extract_vars(tree.left).union(extract_vars(tree.right))
    elif isinstance(tree, Successor):
        return vars.union(extract_vars(tree.sub_term))
def canonicalize(tree):
    if isinstance(tree, Eq):
        if(isinstance(tree.left, Successor) and isinstance(tree.right,Successor)):
            return canonicalize(Eq(tree.left.sub_term,tree.right.sub_term))
        elif isinstance(tree.left,Successor):
            return Eq(tree.right, tree.left)
        elif(isinstance(tree.left, Zero)):
            if(isinstance(tree.right, Zero)):
                return tree 
            elif(isinstance(tree.right, FVar)):
                return Eq(tree.right, tree.left)
        else:
            return tree
    elif isinstance(tree, Lt): # Cant reorder, but can remove extraneous successors
        if(isinstance(tree.left, Successor) and isinstance(tree.right,Successor)):
            return canonicalize(Lt(tree.left.sub_term, tree.right.sub_term))
        else: 
            return tree
    elif isinstance(tree, Negate):
        if isinstance(tree.sub_term, Negate): # Remove double negation 
            return canonicalize(tree.sub_term.sub_term)
        else:
            return tree
    elif isinstance(tree, QuantifiedExpr):
        return QuantifiedExpr(tree.bound_var, canonicalize(tree.expression), tree.order, tree.quantifier)
    else: 
        return tree

def s1s_parse(program):
    return canonicalize(construct_typed_ast(parser.parse(program).children[0]))

if __name__ == "__main__":
    tree = parser.parse(toy_prog)
    pretty_print(tree,0)

    typed_tree = construct_typed_ast(tree.children[0])
    print(typed_tree.to_string())
    print(extract_vars(typed_tree))
