from lib.grammar import *
from lib.automaton import *

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-f","--file",type=str, help="File to read formula from")


args = parser.parse_args()
if args.file is not None:
    prog = open(args.file, "r").read()
else:
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