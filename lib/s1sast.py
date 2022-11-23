class AST:
    def print(self):
        return "ERROR"

class FVar(AST):
    def __init__(self, name):
        self.var_name = name
    def to_string(self):
        return f"FVAR({self.var_name})"
    def get_order(self):
        return 1
class SVar(AST):
    def __init__(self, name):
        self.var_name = name
    def to_string(self):
        return f"SVAR({self.var_name})"
    def get_order(self):
        return 2

class Zero(AST):
    def __init__(self):
        pass 
    def to_string(self):
        return "0"
class Successor(AST):
    def __init__(self, subterm):
        self.sub_term = subterm
    def to_string(self):
        return f"S({self.sub_term.to_string()})"

class QuantifiedExpr(AST):
    def __init__(self, bound, expr, order, quant):
        self.bound_var = bound 
        self.expression = expr 
        self.order = order 
        self.quantifier = quant 
    def to_string(self):
        return f"QUANTIFIED, ORDER {self.order}({self.quantifier} {self.bound_var.to_string()} . {self.expression.to_string()})"

class Eq(AST):
    def __init__(self, l,r):
        self.left = l 
        self.right = r 
    def to_string(self):
        return f"EQ({self.left.to_string()},{self.right.to_string()})"

class In(AST):
    def __init__(self, l,r):
        self.left = l 
        self.right = r 
    def to_string(self):
        return f"IN({self.left.to_string()},{self.right.to_string()})"

class Lt(AST):
    def __init__(self, l,r):
        self.left = l 
        self.right = r 
    def to_string(self):
        return f"LT({self.left.to_string()},{self.right.to_string()})"

class Negate(AST):
    def __init__(self,t):
        self.sub_term = t 
    def to_string(self):
        return f"NOT({self.sub_term.to_string()})"

class Or(AST):
    def __init__(self,left,right):
        self.left = left 
        self.right = right 
    def to_string(self):
        return f"OR({self.left.to_string()},{self.right.to_string()})"

class And(AST):
    def __init__(self,left,right):
        self.left = left 
        self.right = right 
    def to_string(self):
        return f"AND({self.left.to_string()},{self.right.to_string()})"