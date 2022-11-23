# Unit Tests for S1S Model checker
import os, sys, inspect

# Add parent directory to path, to access library
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 

import lib.automaton as automaton
import lib.grammar as grammar
import unittest

def is_sat(prop):
    aut = automaton.ast_to_automaton(grammar.s1s_parse(prop))
    return not aut.is_empty()

class TestAtomicPropositions(unittest.TestCase):
    def test_x_equal_y(self):
        self.assertTrue(is_sat("x=y"))
    def test_x_equal_zero(self):
        self.assertTrue(is_sat("x=0"))
        self.assertTrue(is_sat("0=x"))
    def test_x_equal_S0(self):
        self.assertTrue(is_sat("x=S0"))
    def test_x_eq_sy(self):
        self.assertTrue(is_sat("x=Sy"))
    def test_x_eq_ssy(self):
        self.assertTrue(is_sat("x=SSy"))
    def test_zero(self):
        self.assertTrue(is_sat("0=0"))
    def test_zero_lt(self):
        self.assertFalse(is_sat("0<0"))
    def test_x_lt_y(self):
        self.assertTrue(is_sat("x<y"))
    def test_x_lt_sy(self):
        self.assertTrue(is_sat("x<Sy"))
    def test_zero_gt_szero(self):
        self.assertFalse(is_sat("0>S0"))
    def test_x_in_s(self):
        self.assertTrue(is_sat("x in X"))

class TestConnectives(unittest.TestCase):
    def test_x_neq_y(self):
        self.assertTrue(is_sat("x!=y"))
    def test_x_neq_eq_y(self):
        self.assertFalse(is_sat("x=y & x!=y"))
    def test_x_eq_y_impl_x_neq_y(self):
        self.assertTrue(is_sat("x = y -> x != y"))

class TestBound(unittest.TestCase):
    def test_bound_exist(self):
        tree = grammar.s1s_parse("exists x.x=y")
        bound = [x for x in grammar.extract_vars(tree) if automaton.is_bound(x,tree)]
        self.assertTrue('x' in bound)
        self.assertFalse('y' in bound)
    def test_bind_type_exist(self):
        tree = grammar.s1s_parse("exists x.x=y")
        self.assertTrue(automaton.get_bind_type('x', tree) == 'exists')
    def test_bound_all(self):
        tree = grammar.s1s_parse("forall x.x=y")
        bound = [x for x in grammar.extract_vars(tree) if automaton.is_bound(x,tree)]
        self.assertTrue('x' in bound)
        self.assertFalse('y' in bound)
    def test_bind_type_forall(self):
        tree = grammar.s1s_parse("forall x.x=y")
        self.assertTrue(automaton.get_bind_type('x', tree) == 'forall')

class TestVarExtraction(unittest.TestCase):
    def test_extract_vars(self):
        tree = grammar.s1s_parse("forall S. exists y. forall x. x in S -> y <= x")
        expected = ['S', 'y','x']
        for v in expected:
            self.assertTrue(v in grammar.extract_vars(tree))
if __name__ == "__main__":
    unittest.main()