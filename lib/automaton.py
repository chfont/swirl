import buddy
import spot

from lib.s1sast import *
import lib.grammar as grammar

def construct_automaton(tree, vars,bound_vars,bind_types, ap_bdds = None, var_map = None, ap_nums = None, bdict = None, base=False):
    if bdict is None:
        bdict = spot.make_bdd_dict()
    aut = spot.make_twa_graph(bdict)
    
    if var_map is None:
        ap_nums = [(x,aut.register_ap(x)) for x in vars]
        ap_nums = dict(ap_nums)
        ap_bdds = [buddy.bdd_ithvar(ap_nums[x]) for x in vars]
        var_map = dict(zip(vars, ap_bdds))
    else: 
        ap_nums = [(x,aut.register_ap(x)) for x in var_map]
        ap_nums = dict(ap_nums)
        ap_bdds = [buddy.bdd_ithvar(ap_nums[x]) for x in var_map]
        var_map = dict(zip(vars, ap_bdds))

    def project(bdd):
        return project_if_bound(bound_vars, bdd, var_map, bind_types)
    if isinstance(tree, Eq):
        if isinstance(tree.left, Zero):
            # after canonicalization, must have 0 = 0 or 0 = S(x)
            if isinstance(tree.right, Successor): # 0 = Sx - False
                aut.new_states(2)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")
                p1 = buddy.bdd_ithvar(aut.register_ap("p1"))
                aut.new_edge(0,0, p1 & -p1, [0])
            else:
                aut.new_states(1)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")
                p1 = buddy.bdd_ithvar(aut.register_ap("p1"))
                aut.new_edge(0,0, p1 | -p1, [0])
        elif isinstance(tree.left, FVar):
            if isinstance(tree.right, FVar):
                #fvar = fvar case
                aut.new_states(2)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")

                p1 = var_map[tree.left.var_name]
                p2 = var_map[tree.right.var_name]

                aut.new_edge(0,0, project(-p1 & -p2))
                aut.new_edge(0,1, project(p1 & p2))
                aut.new_edge(1,1, project(-p1 & -p2),[0] )
            elif isinstance(tree.right, Zero):
                # fvar = 0 
                aut.new_states(2)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")

                p1 = var_map[tree.left.var_name]
                aut.new_edge(0,1, project(p1))
                aut.new_edge(1,1, project(p1 | -p1), [0])
            else: # successor function on right
                y = tree.right
                x = tree.left
                count = 0 
                while isinstance(y,Successor):
                    y = y.sub_term
                    count += 1
                # either y = 0 or a var name
                if isinstance(y, Zero):
                    #x = count
                    aut.new_states(count + 2)
                    aut.set_init_state(0)
                    aut.prop_state_acc(True)
                    aut.set_acceptance(1, "Inf(0)")
                    p1 = var_map[x.var_name]
                    for i in range(0,count):
                        aut.new_edge(i,i+1, project(-p1))    
                    aut.new_edge(count, count+1, project(p1))
                    aut.new_edge(count+1,count+1, project(-p1), [0])
                else: 
                    # x = y + count
                    aut.new_states(count+2)
                    aut.set_init_state(0)
                    aut.prop_state_acc(True)
                    aut.set_acceptance(1, "Inf(0)")
                    p1 = var_map[x.var_name]
                    p2 = var_map[y.var_name]
                    aut.new_edge(0,0, project(-p1 & -p2))
                    aut.new_edge(0,1, project(-p1 & p2))
                    for i in range(0, count-1):
                        aut.new_edge(1+i,2+i, project(-p1 & -p2))
                    aut.new_edge(count, count+1,project(p1 & -p2))
                    aut.new_edge(count+1,count+1, project(-p1 & -p2), [0])

    elif isinstance(tree, In):
        if isinstance(tree.left, Zero):
            # 0 in set X
            x = var_map[tree.right.var_name]
            aut.new_states(2)
            aut.set_init_state(0)
            aut.prop_state_acc(True)
            aut.set_acceptance(1, "Inf(0)")

            aut.new_edge(0,1, project(x))
            aut.new_edge(1,1,project(x | -x), [0])
        elif isinstance(tree.left, FVar):
            s = var_map[tree.right.var_name]
            x = var_map[tree.left.var_name]
            aut.new_states(2)
            aut.set_init_state(0)
            aut.prop_state_acc(True)
            aut.set_acceptance(1, "Inf(0)")

            aut.new_edge(0,0, project(-x))
            aut.new_edge(0,1, project(x & s))
            aut.new_edge(1,1, project(x | -x),[0])
        else: # is Successor of some term
            y = tree.left 
            count = 0
            while isinstance(y,Successor):
                y = y.sub_term
                count += 1
            if isinstance(y,Zero):
                # count in s
                aut.new_states(2+count)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")
                s = var_map[tree.right.var_name]
                for i in range(0,count):
                    aut.new_edge(0+i, 1+i, project(-s | s))
                aut.new_edge(count, count+1, s)
                aut.new_edge(count+1, count+1, project(s | -s), [0])
            else: #x + count in s
                aut.new_states(2+count)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")

                x = var_map[y.var_name]
                s = var_map[tree.right.var_name]
                aut.new_edge(0,0, project(-x))
                aut.new_edge(0,1, project(x))
                for i in range(0,count-1):
                    aut.new_edge(1+i, 2+i, -s | s)
                aut.new_edge(count, count+1, project(s))
                aut.new_edge(count+1,count+1, project(s | -s), [0])
    elif isinstance(tree, Lt):
        if isinstance(tree.right, Zero):
            #x < 0: false 
            aut.new_states(2)
            aut.set_init_state(0)
            aut.prop_state_acc(True)
            aut.set_acceptance(1, "Inf(0)")
            p1 = buddy.bdd_ithvar(aut.register_ap("p1"))
            aut.new_edge(0,0, project(p1 & -p1), [0])
        elif isinstance(tree.left, Zero): #TODO Fix
            #0 < y: true
            aut.new_states(3)
            aut.set_init_state(0)
            aut.prop_state_acc(True)
            aut.set_acceptance(1, "Inf(0)")
            p1 = buddy.bdd_ithvar(aut.register_ap("p1"))
            aut.new_edge(0,1, project(p1))
            aut.new_edge(0,2, project(-p1))
            aut.new_edge(2,2, project(p1 | -p1), [0])
            aut.new_edge(1,1, project(p1 | -p1))
        elif isinstance(tree.right, FVar) and isinstance(tree.left, FVar):
            # x < y
            p1 = var_map[tree.left.var_name]
            p2 = var_map[tree.right.var_name]

            aut.new_states(3)
            aut.set_init_state(0)
            aut.prop_state_acc(True)
            aut.set_acceptance(1, "Inf(0)")

            aut.new_edge(0,0, project(-p1 & -p2))
            aut.new_edge(0,1, project(p1 & -p2))
            aut.new_edge(1,1, project(-p1 & -p2))
            aut.new_edge(1,2, project(-p1 & p2))
            aut.new_edge(2,2, project(-p1 & -p2), [0])
        elif isinstance(tree.left, FVar):
            # x < S(something) - find number of successors:
            y = tree.right
            x = tree.left
            count = 0 
            while isinstance(y,Successor):
                y = y.sub_term
                count += 1
            if isinstance(y, FVar): #TODO: redo x <  y + count
                p1 = var_map[x.var_name]
                p2 = var_map[y.var_name]
                aut.new_states(2+count)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")
                aut.new_edge(0,0, project(-p1 & -p2))
                aut.new_edge(0,count+1, project(p1))
                aut.new_edge(0,1,project(-p1 & p2))
                for i in range(1,count):
                    aut.new_edge(i,i+1, project(-p1))
                    aut.new_edge(i,count+1, project(p1))
                aut.new_edge(count, count, project(-p1 | p1))
                aut.new_edge(count+1, count+1, project(-p1 | p1), [0])
            else: # x < count
                aut.new_states(2+count)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")
                p1 = var_map[x.var_name]
                for i in range(0, count):
                    aut.new_edge(i, i+1, project(-p1))
                    aut.new_edge(i, count+1, project(p1))
                aut.new_edge(count+1, count+1, project(p1 | -p1), [0])
                aut.new_edge(count,count, project(p1|-p1))
        else: # Left is successor. By canonicalization, right must be FVar
            x = tree.left 
            y = tree.right
            count = 0
            while isinstance(x, Successor):
                count += 1
                x = x.sub_term
            if isinstance(x, Zero):
                # count < y 
                aut.new_states(count+3)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")
                p1 = var_map[y.var_name]
                for i in range(0, count+1):
                    aut.new_edge(i,i+1, project(-p1))
                    aut.new_edge(i, count+2, project(p1))
                aut.new_edge(count+1,count+1, project(-p1 | p1), [0])
            else:#count + x < y TODO: fix
                aut.new_states(count+3)
                aut.set_init_state(0)
                aut.prop_state_acc(True)
                aut.set_acceptance(1, "Inf(0)")
                x = var_map[x.var_name]
                y = var_map[y.var_name]
                aut.new_edge(0,0, project(-x & -y))
                aut.new_edge(0, count+2, project(y))
                aut.new_edge(0,1, project(x & -y))
                for i in range(1, count+1):
                    aut.new_edge(i,i+1, project(-y))
                    aut.new_edge(i, count+2, project(y))
                aut.new_edge(count+1, count+1, project(y | -y), [0])
                aut.new_edge(count+2, count+2, project(y | -y))

    elif isinstance(tree, And):
        aut = spot.product(construct_automaton(tree.left, vars, bound_vars,bind_types, ap_bdds, var_map,ap_nums, bdict), 
        construct_automaton(tree.right,vars,bound_vars,bind_types, ap_bdds,var_map,ap_nums, bdict))
    elif isinstance(tree, Or):
        aut = spot.sum(construct_automaton(tree.left, vars,bound_vars, bind_types, ap_bdds, var_map,ap_nums, bdict), 
        construct_automaton(tree.right,vars,bound_vars,bind_types, ap_bdds,var_map,ap_nums, bdict))
    elif isinstance(tree, Negate):
        aut = spot.degeneralize(spot.to_generalized_buchi(spot.dualize(construct_automaton(tree.sub_term, vars,bound_vars,bind_types,ap_bdds, var_map, ap_nums, bdict))))
    elif isinstance(tree, QuantifiedExpr):
        aut = construct_automaton(tree.expression,vars,bound_vars,bind_types,ap_bdds, var_map,ap_nums,  bdict)

        

    # aut has been setup
    if base:
        principle_automata = [build_principle_automaton(var_map[x],bdict) for x in var_map if is_first_order(x) and not x in bound_vars]
        for a in principle_automata:
            aut = spot.product(aut,a)
    return aut

def is_first_order(x):
    return x[0].islower()

# Automaton that says x in O*10^w
def build_principle_automaton(bdd, bdict): 
    aut = spot.make_twa_graph(bdict)
    aut.new_states(2)
    aut.set_init_state(0)
    aut.prop_state_acc(True)
    aut.set_acceptance(1, "Inf(0)")

    aut.new_edge(0,0, -bdd)
    aut.new_edge(0,1, bdd)
    aut.new_edge(1,1, -bdd, [0])
    return aut

def ast_to_automaton(canonical_tree):
    vars = list(grammar.extract_vars(canonical_tree))
    vars.sort()
    bound_vars = [x for x in vars if is_bound(x,canonical_tree)]
    bind_types = dict([(x, get_bind_type(x, canonical_tree)) for x in bound_vars])
    return construct_automaton(canonical_tree, vars,bound_vars,bind_types,base=True)

def get_bind_type(var, expr): # assume var is bound, is it universal or existential?
    match expr:
        case QuantifiedExpr():
            if expr.bound_var.var_name == var:
                return expr.quantifier
            else: 
                return get_bind_type(var, expr.expression)
        case Negate(sub_term=sub):
            return get_bind_type(var, sub)
        case And(left=left,right=right):
            v = get_bind_type(var, left) 
            if v is None: 
                return get_bind_type(var, right)
            else: 
                return v
        case Or(left=left,right=right):
            v = get_bind_type(var, left) 
            if v is None: 
                return get_bind_type(var, right)
            else: 
                return v
        case _: 
            return None

def is_bound(var, expr):
    match expr:
        case QuantifiedExpr():
            if expr.bound_var.var_name == var:
                return True
            else:
                return is_bound(var, expr.expression)
        case Negate(sub_term=sub):
            return is_bound(var,sub)
        case And(left=left,right=right):
            return is_bound(var,left) | is_bound(var, right)
        case Or(left=left,right=right):
            return is_bound(var,left) | is_bound(var, right)
        case e:
            return False

def project_if_bound(bound_vars, bdd, var_map, bind_types):
    res = bdd 
    for v in bound_vars:
        if bind_types[v] == 'exists':
            res = buddy.bdd_exist(var_map[v], res)
        else:
            res = buddy.bdd_forall(var_map[v],res)
    return res
