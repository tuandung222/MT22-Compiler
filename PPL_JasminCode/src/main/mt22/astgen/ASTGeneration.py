#2010013

from MT22Visitor import MT22Visitor
from MT22Parser import MT22Parser
from AST import *



class ASTGeneration(MT22Visitor):
    def visitProgram(self, ctx: MT22Parser.ProgramContext):
        return Program(self.visit(ctx.decl_list()))

    def visitDecl_list(self, ctx: MT22Parser.Decl_listContext):
        return self.visit(ctx.getChild(0)) + (self.visit(ctx.getChild(1)) if ctx.decl_list() else [])

    def visitDecl(self, ctx: MT22Parser.DeclContext):
        return self.visit(ctx.getChild(0))

    def visitVar_decl(self, ctx: MT22Parser.Var_declContext):
        if ctx.COLON():
            id_list = self.visit(ctx.id_list())
            var_type = self.visit(ctx.var_type())
            return [VarDecl(x.name, var_type, None) for x in id_list]
        else:
            return self.visit(ctx.getChild(0))

    def visitFunc_decl(self, ctx: MT22Parser.Func_declContext):
        name = ctx.getChild(0).getText()
        return_type = self.visit(ctx.getChild(3))
        params = self.visit(ctx.param_list())
        inherit = None if not ctx.INHERIT() else ctx.ID(1).getText()
        body = self.visit(ctx.block_stmt())
        return [FuncDecl(name, return_type, params, inherit, body)]

    def visitId_list(self, ctx: MT22Parser.Id_listContext):
        id_ret = [Id(ctx.ID().getText())]
        if ctx.id_list():
            id_ret += self.visit(ctx.id_list())
        return id_ret

    def visitVar_type(self, ctx: MT22Parser.Var_typeContext):
        return self.visit(ctx.getChild(0))

    def visitFull_var_decl(self, ctx: MT22Parser.Full_var_declContext):
        if not ctx.COMMA():
            type = self.visit(ctx.var_type())
            init = self.visit(ctx.expr())
            return [VarDecl(ctx.ID().getText(), type, init)]
        else:
            list_var = self.visit(ctx.full_var_decl())
            init_list = [x.init for x in list_var] + [self.visit(ctx.expr())]
            name_list = [ctx.ID().getText()] + [x.name for x in list_var]
            type = list_var[0].typ
            zip_list = list(zip(name_list, init_list))
            return [VarDecl(x[0], type, x[1]) for x in zip_list]

    def visitExpr(self, ctx: MT22Parser.ExprContext):
        return self.visit(ctx.getChild(0))

    def visitFunc_ret_type(self, ctx: MT22Parser.Func_ret_typeContext):
        return self.visit(ctx.getChild(0))

    def visitParam_list(self, ctx: MT22Parser.Param_listContext):
        return self.visit(ctx.getChild(1))

    def visitParam_list_body(self, ctx: MT22Parser.Param_list_bodyContext):
        return self.visit(ctx.getChild(0)) if ctx.getChildCount() > 0 else []

    def visitParam_prime(self, ctx: MT22Parser.Param_primeContext):
        ret = [self.visit(ctx.getChild(0))]
        ret += self.visit(ctx.param_prime()) if ctx.getChildCount() != 1 else []
        return ret

    def visitParam_decl(self, ctx: MT22Parser.Param_declContext):
        name = ctx.ID().getText()
        typ = self.visit(ctx.para_type())
        out = ctx.OUT() is not None
        inherit = ctx.INHERIT() is not None
        return ParamDecl(name, typ, out, inherit)

    def visitStmt(self, ctx: MT22Parser.StmtContext):
        return self.visit(ctx.getChild(0))

    def visitMatch_stmt(self, ctx: MT22Parser.Match_stmtContext):
        if not ctx.IF():
            return self.visit(ctx.getChild(0))
        else:
            cond = self.visit(ctx.sub_expr())
            tstmt = self.visit(ctx.match_stmt(0))
            fstmt = self.visit(ctx.match_stmt(1))
            return IfStmt(cond, tstmt, fstmt)

    def visitUnmatch_stmt(self, ctx: MT22Parser.Unmatch_stmtContext):
        if not ctx.ELSE():
            cond = self.visit(ctx.sub_expr())
            tstmt = self.visit(ctx.stmt())
            return IfStmt(cond, tstmt)
        else:
            cond = self.visit(ctx.sub_expr())
            tstmt = self.visit(ctx.match_stmt())
            fstmt = self.visit(ctx.unmatch_stmt())
            return IfStmt(cond, tstmt, fstmt)

    def visitAssign_stmt(self, ctx: MT22Parser.Assign_stmtContext):
        lhs = self.visit(ctx.lhs())
        rhs = self.visit(ctx.expr())
        return AssignStmt(lhs, rhs)

    def visitCall_stmt(self, ctx: MT22Parser.Call_stmtContext):
        name = ctx.ID().getText()
        args = self.visit(ctx.expr_list())
        return CallStmt(name, args)

    def visitReturn_stmt(self, ctx: MT22Parser.Return_stmtContext):
        expr = None
        if ctx.getChildCount() == 3:
            expr = self.visit(ctx.expr())
        return ReturnStmt(expr)

    # def visitIf_stmt(self, ctx: MT22Parser.If_stmtContext):
    #     cond = self.visit(ctx.expr())
    #     tstmt = self.visit(ctx.stmt(0))
    #     if ctx.ELSE():
    #         fstmt = self.visit(ctx.stmt(1))
    #     else:
    #         fstmt = None
    #     return IfStmt(cond, tstmt, fstmt)

    def visitFor_stmt(self, ctx: MT22Parser.For_stmtContext):
        cond = self.visit(ctx.expr(1))
        upd = self.visit(ctx.expr(2))
        stmt = self.visit(ctx.stmt())
        init = AssignStmt(self.visit(ctx.getChild(2)), self.visit(ctx.expr(0)))
        return ForStmt(init, cond, upd, stmt)

    def visitWhile_stmt(self, ctx: MT22Parser.While_stmtContext):
        cond = self.visit(ctx.expr())
        stmt = self.visit(ctx.stmt())
        return WhileStmt(cond, stmt)

    def visitDo_while_stmt(self, ctx: MT22Parser.Do_while_stmtContext):
        cond = self.visit(ctx.expr())
        stmt = self.visit(ctx.stmt())
        return DoWhileStmt(cond, stmt)

    def visitBlock_stmt(self, ctx: MT22Parser.Block_stmtContext):
        return BlockStmt(self.visit(ctx.getChild(1)))

    def visitContinue_stmt(self, ctx: MT22Parser.Continue_stmtContext):
        return ContinueStmt();

    def visitBreak_stmt(self, ctx: MT22Parser.Break_stmtContext):
        return BreakStmt()


    def visitStov_list(self, ctx: MT22Parser.Stov_listContext):
        if ctx.stov():
            if isinstance(self.visit(ctx.stov()), list):
                return self.visit(ctx.stov()) + self.visit(ctx.stov_list())
            else:
                return [self.visit(ctx.stov())] + self.visit(ctx.stov_list())
        else:
            return []

    def visitStov(self, ctx: MT22Parser.StovContext):
        return self.visit(ctx.getChild(0))

    def visitLhs(self, ctx: MT22Parser.LhsContext):
        if ctx.ID():
            return Id(ctx.ID().getText())
        else:
            return self.visit(ctx.getChild(0))


    def visitExpr_list(self, ctx: MT22Parser.Expr_listContext):
        return self.visit(ctx.getChild(0)) if ctx.exprprime() else []

    def visitExprprime(self, ctx: MT22Parser.Expr_listContext):
        first = [self.visit(ctx.getChild(0))]
        second = self.visit(ctx.getChild(2)) if ctx.exprprime() else []
        return first + second

    def visitExpr0(self, ctx: MT22Parser.Expr0Context):
        if ctx.getChildCount() == 3:
            left = self.visit(ctx.getChild(0))
            right = self.visit(ctx.getChild(2))
            op = ctx.getChild(1).getText()
            return BinExpr(op, left, right)
        else:
            return self.visit(ctx.getChild(0))

    def visitExpr1(self, ctx: MT22Parser.Expr1Context):
        if ctx.getChildCount() == 3:
            left = self.visit(ctx.getChild(0))
            right = self.visit(ctx.getChild(2))
            op = ctx.getChild(1).getText()
            return BinExpr(op, left, right)
        else:
            return self.visit(ctx.getChild(0))

    def visitExpr2(self, ctx: MT22Parser.Expr2Context):
        if ctx.getChildCount() == 3:
            left = self.visit(ctx.getChild(0))
            right = self.visit(ctx.getChild(2))
            op = ctx.getChild(1).getText()
            return BinExpr(op, left, right)
        else:
            return self.visit(ctx.getChild(0))

    def visitExpr3(self, ctx: MT22Parser.Expr3Context):
        if ctx.getChildCount() == 3:
            left = self.visit(ctx.getChild(0))
            right = self.visit(ctx.getChild(2))
            op = ctx.getChild(1).getText()
            return BinExpr(op, left, right)
        else:
            return self.visit(ctx.getChild(0))

    def visitExpr4(self, ctx: MT22Parser.Expr4Context):
        if ctx.getChildCount() == 3:
            left = self.visit(ctx.getChild(0))
            right = self.visit(ctx.getChild(2))
            op = ctx.getChild(1).getText()
            return BinExpr(op, left, right)
        else:
            return self.visit(ctx.getChild(0))

    def visitExpr5(self, ctx: MT22Parser.Expr5Context):
        if ctx.getChildCount() == 2:
            val = self.visit(ctx.getChild(1))
            op = ctx.getChild(0).getText()
            return UnExpr(op, val)
        else:
            return self.visit(ctx.getChild(0))

    def visitExpr6(self, ctx: MT22Parser.Expr6Context):
        if ctx.getChildCount() == 2:
            val = self.visit(ctx.getChild(1))
            op = ctx.getChild(0).getText()
            return UnExpr(op, val)
        else:
            return self.visit(ctx.getChild(0))

    def visitExpr7(self, ctx: MT22Parser.Expr7Context):
        if not ctx.ID():
            return self.visit(ctx.getChild(0))
        else:
            return Id(ctx.getChild(0).getText())

    def visitFunc_call_expr(self, ctx: MT22Parser.Func_call_exprContext):
        return FuncCall(ctx.ID().getText(), self.visit(ctx.expr_list()))


    def visitConstant(self, ctx: MT22Parser.ConstantContext):
        if ctx.STRINGLIT():
            return StringLit(ctx.STRINGLIT().getText())
        elif ctx.INTLIT():
            return IntegerLit(int(ctx.INTLIT().getText()))
        elif ctx.FLOATLIT():
            return FloatLit(float(ctx.FLOATLIT().getText()))
        elif ctx.BOOLEANLIT():
            return BooleanLit(ctx.BOOLEANLIT().getText() == "true")
        else:
            return self.visit(ctx.getChild(0))

    def visitArray_lit(self, ctx: MT22Parser.Array_litContext):
        return ArrayLit(self.visit(ctx.expr_list()))



    def visitSub_expr(self, ctx: MT22Parser.Sub_exprContext):
        return self.visit(ctx.getChild(1))

    def visitIndex_operator(self, ctx: MT22Parser.Index_operatorContext):
        return self.visit(ctx.getChild(1))


    def visitAtomic_type(self, ctx: MT22Parser.Atomic_typeContext):
        if ctx.INTEGER():
            return IntegerType()
        elif ctx.FLOAT():
            return FloatType()
        elif ctx.STRING():
            return StringType()
        elif ctx.BOOLEAN():
            return BooleanType()


    def visitVoid_type(self, ctx: MT22Parser.Void_typeContext):
        return VoidType();

    def visitAuto_type(self, ctx: MT22Parser.Auto_typeContext):
        return AutoType();

    def visitArray_type(self, ctx: MT22Parser.Array_typeContext):
        dimensions = self.visit(ctx.getChild(1))
        typ = self.visit(ctx.getChild(3))
        return ArrayType(dimensions, typ)

    def visitDimension(self, ctx: MT22Parser.DimensionContext):
        return [x.val for x in self.visit(ctx.intlit_list())]


    def visitIntlit_list(self, ctx: MT22Parser.Intlit_listContext):
        intlit = [IntegerLit(int(ctx.INTLIT().getText()))]
        ret = intlit
        if ctx.intlit_list():
            ret += self.visit(ctx.intlit_list())
        return ret

    def visitIndex_expr(self, ctx: MT22Parser.Index_exprContext):
        return ArrayCell(ctx.ID().getText(), self.visit(ctx.getChild(1)))
