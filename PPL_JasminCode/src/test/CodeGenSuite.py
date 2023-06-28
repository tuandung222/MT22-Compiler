import unittest
from TestUtils import TestCodeGen
from AST import *


class CheckCodeGenSuite(unittest.TestCase):

        
    def test3(self):
        input = """
            
            a: integer = 1;
            b: auto = 3;
            c: auto = {1,2,3};

            fibo: function auto(inherit out n: integer){
                n = 0;
                if (n <= 1) return n;
                else return fibo(n - 1) + fibo(n - 2); 
            }  
            fibo2: function auto(p: integer) inherit fibo{
                super(p);
                n = 10;
                if (n <= 1) return n;
                else return fibo(n - 1) + fibo(n - 2); 
            }  
            m: integer = 1;
            main : function void(){
                for (a = 1, a < 2000, a * 2) {
                }
                printInteger(c[0]);
            }  
        """
        expect = '2079'
        self.assertTrue(TestCodeGen.test(input,expect,902))
    


