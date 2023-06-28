from Utils import *
from Visitor import *
from StaticCheck import StaticChecker
from StaticError import *
from TACGenerator import *
from abc import ABC, abstractmethod
from AST import *

class CodeGenerator(Utils):
    def __init__(self):
        pass

    def init(self):
        pass

    def gen(self, ast, dir_):
        gl = self.init()
        gc = CodeGenVisitor(ast, gl, dir_)
        gc.visit(ast, None)

class CodeGenVisitor(BaseVisitor, Utils):
    def __init__(self, astTree, env, dir_):
        self.astTree = StaticChecker(astTree).check()
        self.path = dir_
        self.tac = TACGenerator(self.path + "/" + "main" + ".asm")

    def visitProgram(self, ast, c = None):
        c = [[]]
        for x in ast.decls:
            if type(x) is VarDecl:
                res = self.tac.getNewGlobalVar(x.name)
                c[0].append(res)
                if x.init:
                    sym = self.visit(x.init, c)
                    self.tac.genAssign(res, sym)

        self.tac.genPreamble()
        self.visit(self.lookup( "main", ast.decls, lambda u: u.name), c)
        [self.visit(x, c) for x in ast.decls if type(x) is FuncDecl and x.name != "main"]
        self.tac.writeFile()

    def visitFuncDecl(self, ast, o):
        o = [[]] + o
        self.tac.genLabel(ast.name)
        self.tac.genBeginFunc()
        list_param_sym = [self.visitParamDecl(x, o) for x in ast.params]
        self.tac.genReceiveParams(list_param_sym)
        self.visit(ast.body, o)
        if ast.return_type is VoidType():
            self.tac.genReturn(None)
        # self.tac.genPopAllStack()


    def visitCallStmt(self, ast, o):
        for index, x in enumerate(ast.args):
            sym = self.visit(x, o)
            self.tac.genPushParam(sym, index)
        self.tac.genLCall(ast.name, False)
        # self.tac.genPopStack(len(ast.args) * 4)

    def visitFuncCall(self, ast, o):
        for index, x in enumerate(ast.args):
            sym = self.visit(x, o)
            self.tac.genPushParam(sym, index)
        res = self.tac.genLCall(ast.name, True)
        # self.tac.genPopStack(len(ast.args) * 4 + 8)
        return res

    def visitBlockStmt(self, ast, o):
        num_var = len([x for x in ast.body if isinstance(x, VarDecl)])
        for x in ast.body:
            if isinstance(x, BlockStmt):
                self.visit(x, [[]] + o)
            else:
                self.visit(x, o)
    
    def visitParamDecl(self, ast, o):
        res = self.tac.getNewLocationOnStack(ast.name)
        o[0] += [res]
        return res

    def visitVarDecl(self, ast, o):
        #Local Only
        o[0] += [self.tac.getNewLocationOnStack(ast.name)]
        if ast.init:
            self.visit(AssignStmt(Id(ast.name), ast.init), o)

    def visitId(self, ast, o):
        res = None
        for lst in o:
            res = self.lookup(ast.name, lst, lambda x: x.name)
            if res: break
        return res
    

    def visitBinExpr(self, ast, o):
        l_sym = self.visit(ast.left, o)
        r_sym = self.visit(ast.right, o)
        return self.tac.genBinaryOp(ast.op, l_sym, r_sym)
    
    def visitAssignStmt(self, ast, o):
        l_sym = self.visit(ast.lhs, o)
        r_sym = self.visit(ast.rhs,o)
        
        self.tac.genAssign(l_sym, r_sym)
    
    def visitReturnStmt(self, ast, o):
        if ast.expr:
            res = self.visit(ast.expr, o)
            self.tac.genReturn(res)
        else:
            self.tac.genReturn(None)
    
    def visitIntegerLit(self, ast, o):
        temp_sym = self.tac.getTempVar()
        self.tac.genLoadConstant(temp_sym, ast.val)
        return temp_sym

    def visitFloatLit(self, ast, o):
        temp_sym = self.tac.getTempVar()
        self.tac.genLoadConstant(temp_sym, ast.val)
        return temp_sym 
    
    def visitBooleanLit(self, ast, o):
        temp_sym = self.tac.getTempVar()
        val = 0 if ast.val == False else 1
        self.tac.genLoadConstant(temp_sym, val)
        return temp_sym

    def visitUnExpr(self, ast, o):
        if ast.op == '!':
            left = self.visit(IntegerLit(1), o)
            right = self.visit(ast.val, o)
            return self.tac.genBinaryOp('-', left, right)
        elif ast.op == '-':
            left = self.visit(IntegerLit(0), o)
            right = self.visit(ast.val, o)
            return self.tac.genBinaryOp('-', left, right)
            
    def visitIfStmt(self,ast,o):
        expr = ast.cond
        true_stmt = ast.tstmt
        false_stmt = ast.fstmt
        end_label = self.tac.getNewLabel()
        expr_sym = self.visit(expr, o)
        if false_stmt:
            else_label = self.tac.getNewLabel()
            self.tac.genIfZ(expr_sym, else_label)
            self.visit(true_stmt, o)
            self.tac.genGoto(end_label)
            self.tac.genLabel(else_label)
            self.visit(false_stmt, o)
            self.tac.genLabel(end_label)
        else:
            self.tac.genIfZ(expr_sym, end_label)
            self.visit(true_stmt, o)
            self.tac.genLabel(end_label)
                
    def visitWhileStmt(self,ast,o):
        continue_label = self.tac.createContinueLabel()
        break_label = self.tac.createBreakLabel()
        self.tac.genLabel(continue_label)
        expr_sym = self.visit(ast.cond, o)
        self.tac.genIfZ(expr_sym, break_label)
        self.visit(ast.stmt, o)
        self.tac.genGoto(continue_label)
        self.tac.genLabel(break_label)
        self.tac.exitLoop()
        
    def visitDoWhileStmt(self,ast,o):
        continue_label = self.tac.createContinueLabel()
        break_label = self.tac.createBreakLabel()
        self.tac.genLabel(continue_label)
        self.visit(ast.stmt, o)
        expr_sym = self.visit(ast.cond, o)
        self.tac.genIfZ(expr_sym, break_label)
        self.tac.genGoto(continue_label)
        self.tac.genLabel(break_label)
        self.tac.exitLoop()
        
    def visitForStmt(self, ast, o):
        upd_stmt = AssignStmt(ast.init.lhs, ast.upd)
        continue_label = self.tac.createContinueLabel()
        break_label = self.tac.createBreakLabel()
        self.visit(ast.init, o)
        self.tac.genLabel(continue_label)
        expr_sym = self.visit(ast.cond, o)
        self.tac.genIfZ(expr_sym, break_label)
        self.visit(ast.stmt, o)
        self.visit(upd_stmt, o)
        self.tac.genGoto(continue_label)
        self.tac.genLabel(break_label)
        self.tac.exitLoop()
        
        
    def visitBreakStmt(self, ast, o):
        break_label = self.tac.getBreakLabel()
        self.tac.genGoto(break_label)
        
    def visitConinueStmt(self, ast, o):
        continue_label = self.tac.getContinueLabel()
        self.tac.genGoto(continue_label)
        
    
    
    
    