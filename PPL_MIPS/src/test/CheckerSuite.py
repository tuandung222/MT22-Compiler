import unittest
from TestUtils import TestChecker
from AST import *

class CheckerSuite(unittest.TestCase):
    def test1(self):
        """More complex program"""
        input = """
            main : function void(){
                printInteger(foo());
            }  
            foo: function integer(){
                a: integer = 1;
                for (a = 1, a < 100, a * 2) {
                    if (a > 16) break;
                }
                return a;
            }  
        """
        expect = "Type Mismatch In Statement: FuncCall(putIntLn, [])"
        self.assertTrue(TestChecker.test(input,expect,405))
    