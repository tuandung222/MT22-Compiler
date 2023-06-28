# Generated from main/mt22/parser/MT22.g4 by ANTLR 4.9.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .MT22Parser import MT22Parser
else:
    from MT22Parser import MT22Parser

# This class defines a complete generic visitor for a parse tree produced by MT22Parser.

class MT22Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by MT22Parser#program.
    def visitProgram(self, ctx:MT22Parser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#decl_list.
    def visitDecl_list(self, ctx:MT22Parser.Decl_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#decl.
    def visitDecl(self, ctx:MT22Parser.DeclContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#var_decl.
    def visitVar_decl(self, ctx:MT22Parser.Var_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#full_var_decl.
    def visitFull_var_decl(self, ctx:MT22Parser.Full_var_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#func_decl.
    def visitFunc_decl(self, ctx:MT22Parser.Func_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#param_decl.
    def visitParam_decl(self, ctx:MT22Parser.Param_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#id_list.
    def visitId_list(self, ctx:MT22Parser.Id_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#param_list.
    def visitParam_list(self, ctx:MT22Parser.Param_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#param_list_body.
    def visitParam_list_body(self, ctx:MT22Parser.Param_list_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#param_prime.
    def visitParam_prime(self, ctx:MT22Parser.Param_primeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#stmt.
    def visitStmt(self, ctx:MT22Parser.StmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#match_stmt.
    def visitMatch_stmt(self, ctx:MT22Parser.Match_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#unmatch_stmt.
    def visitUnmatch_stmt(self, ctx:MT22Parser.Unmatch_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#stov.
    def visitStov(self, ctx:MT22Parser.StovContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#stov_list.
    def visitStov_list(self, ctx:MT22Parser.Stov_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#assign_stmt.
    def visitAssign_stmt(self, ctx:MT22Parser.Assign_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#for_stmt.
    def visitFor_stmt(self, ctx:MT22Parser.For_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#while_stmt.
    def visitWhile_stmt(self, ctx:MT22Parser.While_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#do_while_stmt.
    def visitDo_while_stmt(self, ctx:MT22Parser.Do_while_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#block_stmt.
    def visitBlock_stmt(self, ctx:MT22Parser.Block_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#call_stmt.
    def visitCall_stmt(self, ctx:MT22Parser.Call_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#break_stmt.
    def visitBreak_stmt(self, ctx:MT22Parser.Break_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#continue_stmt.
    def visitContinue_stmt(self, ctx:MT22Parser.Continue_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#return_stmt.
    def visitReturn_stmt(self, ctx:MT22Parser.Return_stmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr.
    def visitExpr(self, ctx:MT22Parser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr_list.
    def visitExpr_list(self, ctx:MT22Parser.Expr_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#exprprime.
    def visitExprprime(self, ctx:MT22Parser.ExprprimeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr0.
    def visitExpr0(self, ctx:MT22Parser.Expr0Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr1.
    def visitExpr1(self, ctx:MT22Parser.Expr1Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr2.
    def visitExpr2(self, ctx:MT22Parser.Expr2Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr3.
    def visitExpr3(self, ctx:MT22Parser.Expr3Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr4.
    def visitExpr4(self, ctx:MT22Parser.Expr4Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr5.
    def visitExpr5(self, ctx:MT22Parser.Expr5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr6.
    def visitExpr6(self, ctx:MT22Parser.Expr6Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#expr7.
    def visitExpr7(self, ctx:MT22Parser.Expr7Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#func_call_expr.
    def visitFunc_call_expr(self, ctx:MT22Parser.Func_call_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#constant.
    def visitConstant(self, ctx:MT22Parser.ConstantContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#sub_expr.
    def visitSub_expr(self, ctx:MT22Parser.Sub_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#index_operator.
    def visitIndex_operator(self, ctx:MT22Parser.Index_operatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#array_lit.
    def visitArray_lit(self, ctx:MT22Parser.Array_litContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#var_type.
    def visitVar_type(self, ctx:MT22Parser.Var_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#func_ret_type.
    def visitFunc_ret_type(self, ctx:MT22Parser.Func_ret_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#para_type.
    def visitPara_type(self, ctx:MT22Parser.Para_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#atomic_type.
    def visitAtomic_type(self, ctx:MT22Parser.Atomic_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#array_type.
    def visitArray_type(self, ctx:MT22Parser.Array_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#dimension.
    def visitDimension(self, ctx:MT22Parser.DimensionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#void_type.
    def visitVoid_type(self, ctx:MT22Parser.Void_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#auto_type.
    def visitAuto_type(self, ctx:MT22Parser.Auto_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#intlit_list.
    def visitIntlit_list(self, ctx:MT22Parser.Intlit_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#lhs.
    def visitLhs(self, ctx:MT22Parser.LhsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MT22Parser#index_expr.
    def visitIndex_expr(self, ctx:MT22Parser.Index_exprContext):
        return self.visitChildren(ctx)



del MT22Parser