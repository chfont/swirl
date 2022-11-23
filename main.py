from lib.grammar import *
from lib.automaton import *

prog = input("Enter a formula: ")
tree = s1s_parse(prog)
aut = ast_to_automaton(tree)

if aut.is_empty():
    print("Unsat")
else:
    print("Sat")
    print("HOA Representation:")
    print(aut.to_str("hoa"))
    print("Accepting Word:")
    print(aut.accepting_word())