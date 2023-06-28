# My assignment is based on code of Mr. Nguyen Hua Phung 
# for Extended Assignment for Students of Honors Program Semester 222
# I use Static Checker to infer type for auto, inherit parameter
# I have completed this assignment before deadline of assignment 3

# I have diffulty  in merging my code based on Mr. Nguyen Hua Phung's code and initialize code of Mr. Tran Ngoc Bao Duy
# So this is my ugly solution for this assignment 

'''
 *   @author Nguyen Hua Phung
 *   @version 1.0
 *   23/10/2015
 *   This file provides a simple version of code generator
 *
'''

from StaticError import *
from Emitter import Emitter, MType, Frame

from abc import ABC, abstractmethod
from Visitor import *
from Utils import Utils
from AST import *

class Val(ABC):
    pass

class Index(Val):
    def __init__(self, value):
        #value: Int
        self.value = value

class CName(Val):
    def __init__(self, value):
        #value: String
        self.value = value
        
class Symbol:
    def __init__(self, name, mtype, value=None, func_sym = None):
        self.name = name
        self.mtype = mtype
        self.value = value
        self.func_sym = func_sym

    def __str__(self):
        return "Symbol(" + self.name + "," + str(self.mtype) + ")"
        
#For infer type, deal with auto
class StaticChecker(Visitor, Utils):
    libName = "io"
    global_envi = [
        Symbol("getInt", MType([], IntegerType()),  CName(libName)),
        Symbol("putIntLn", MType([IntegerType()], VoidType()),  CName(libName)),
        Symbol("readInteger", MType([], IntegerType()),  CName(libName)),
        Symbol("printInteger", MType([IntegerType()], VoidType()), CName(libName)),
        Symbol("readFloat", MType([], FloatType()), CName(libName)),
        Symbol("printFloat", MType([FloatType()], VoidType()), CName(libName)),
        Symbol("printString", MType([StringType()], VoidType()), CName(libName)),
        Symbol("readString", MType([], StringType())),
        Symbol("readBoolean", MType([], BooleanType())),
        Symbol("printBoolean", MType([BooleanType()],VoidType()), CName(libName)),
        # Symbol("preventDefault", MType([], VoidType()), CName(libName)),
    ]
    bi_dict = {
        ("::",): {frozenset([StringType]): StringType},
        ("%",): {frozenset([IntegerType]): IntegerType},
        ('+', '-', '*', '/'): {frozenset([IntegerType, FloatType]): FloatType,
                               frozenset([IntegerType]): IntegerType,
                               frozenset([FloatType]): FloatType},
        ('<', '>', '<=', '>='): {frozenset([IntegerType]): BooleanType,
                                 frozenset([FloatType]): BooleanType,
                                 frozenset([IntegerType, FloatType]): BooleanType},
        ('&&', '||'): {frozenset([BooleanType]): BooleanType},
        ('==', '!='): {frozenset([IntegerType, BooleanType]): BooleanType, 
                       frozenset([IntegerType]): BooleanType,
                        frozenset([IntegerType]): BooleanType}
    }

    def __init__(self, ast):
        self.ast = ast
        #3rd argument is ast itself
        self.list_func = [Symbol(x.name,
                                 MType([y.typ for y in x.params], x.return_type),
                                x)
                          for x in ast.decls if isinstance(x, FuncDecl)] + StaticChecker.global_envi
        
        self.global_var = [Symbol(x.name, x.typ, x)
                          for x in ast.decls if isinstance(x, VarDecl)]

    def check(self):
        return self.visit(self.ast, StaticChecker.global_envi)

    def visitProgram(self, ast, context):
        env = [StaticChecker.global_envi]
        for x in ast.decls:
            self.visit(x, env)
            
        sym_main = self.lookup("main", env[-1], lambda z: z.name)
        if not self.lookup("main", env[-1], lambda z: z.name) \
                or not isinstance(sym_main.mtype.rettype, VoidType) \
                or len(sym_main.mtype.partype) != 0:
            raise NoEntryPoint()
        return ast

    def visitFuncDecl(self, ast, context):
        if self.find_sym(ast.name, context):
            raise Redeclared(Function(), ast.name)
        func_sym = self.lookup(ast.name, self.list_func, lambda u: u.name)
        func_env = [[Symbol("function", None, ast)]] + context
        for param in ast.params:
            self.visit(param, func_env)
        if ast.inherit:
            parent_func = self.lookup(ast.inherit, self.list_func, lambda u: u.name)
            
            if parent_func is None:
                raise Undeclared(Function(), ast.inherit)
            func_env[0].append(Symbol("super", MType(parent_func.mtype.partype, VoidType())))
            func_env[0].append(Symbol("preventDefault", MType([], VoidType())))
            if len(func_sym.value.body.body) > 0 and \
                    isinstance(func_sym.value.body.body[0], CallStmt) and \
                    func_sym.value.body.body[0].name == "preventDefault":
                pass
            else:
                # self.visit_ancestors_params(parent_func, func_env, context)
                self.visitDadParamDecls(func_sym, parent_func, func_env)
        self.visit(ast.body, func_env)

        context[0] =  context[0] + [func_sym] 

    def visit_ancestors_params(self, parent_func, func_env, context):
        if self.lookup(parent_func.name, StaticChecker.global_envi, lambda u: u.name):
            return
        for param in parent_func.value.params:
            res = self.lookup(param.name, func_env[0] + StaticChecker.global_envi, lambda u: u.name)
            if res: 
                raise Redeclared(Parameter(), param.name)
            if param.inherit:
                self.visit(param, func_env)
                sym = self.lookup(param.name, func_env[0], lambda u: u.name)
                sym.func_sym = parent_func

                    
    def visitFuncCall(self, ast, context):
        sym = self.find_func_sym(ast.name, context)
        var_sym = self.find_sym(ast.name, context)
        if sym and var_sym and (not isinstance(var_sym.mtype, MType)):
            raise Undeclared(Function(), ast.name)
        # if sym is None and var_sym is None:
        if sym is None:
            raise Undeclared(Function(), ast.name)
        # elif sym is None and var_sym is not None:
        #     raise TypeMismatchInExpression(ast)
        if isinstance(sym.mtype.rettype, VoidType):
            raise TypeMismatchInExpression(ast)
        list_type_param = sym.mtype.partype
        list_pair_typ = self.check_param_list(list_type_param, ast.args, context)
        if list_pair_typ is None:
            raise TypeMismatchInExpression(ast)
        else:
            for i, res in enumerate(list_pair_typ):                 #res: l_type, r_type
                if isinstance(res[0], AutoType):
                    sym.value.params[i].typ = res[1]
                    sym.mtype.partype[i] = res[1]
        return sym.mtype.rettype
    
    def visitCallStmt(self, ast, context):
        sym = self.find_func_sym(ast.name, context)
        var_sym = self.find_sym(ast.name, context)
        if sym and var_sym and (not isinstance(var_sym.mtype, MType)):
            raise Undeclared(Function(), ast.name)
        # if sym is None and var_sym is None:
        if sym is None:
            raise Undeclared(Function(), ast.name)
        # elif sym is None and var_sym is not None:
        #     raise TypeMismatchInStatement(ast)
        if not self.check_param_list(sym.mtype.partype, ast.args, context):
            raise TypeMismatchInStatement(ast)
        list_type_param = sym.mtype.partype
        list_pair_typ = self.check_param_list(list_type_param, ast.args, context)
        if list_pair_typ is None:
            raise TypeMismatchInStatement(ast)
        else:
            for i, res in enumerate(list_pair_typ):
                if isinstance(res[0], AutoType):
                     sym.value.params[i].typ = res[1]
                     sym.mtype.partype[i] = res[1]
        return sym.mtype.rettype

    def visitNotThrowArrayLit(self, ast, context):
        set_typ = set()
        set_dimen = set()
        set_ele_typ = set()
        res_typ = None
        expr_auto = []
        for expr in ast.explist:
            if not isinstance(expr, ArrayLit):
                res_typ2 = self.visit(expr, context)
                if isinstance(res_typ2, AutoType):
                    expr_auto.append(expr)
                    continue
                else:
                    res_typ = res_typ2
            else:
                res_typ2 = self.visitNotThrowArrayLit(expr, context)
                if isinstance(res_typ2, AutoType):
                    expr_auto.append(expr)
                    continue
                else:
                    res_typ = res_typ2
            if isinstance(res_typ, IllegalArrayLiteral):
                return IllegalArrayLiteral(ast)
            typ = type(self.visit(expr, context))
            set_typ.add(typ)
            if not isinstance(res_typ, ArrayType):
                set_dimen.add(0)
            else:
                set_ele_typ.add(type(res_typ.typ))
                set_dimen.add(tuple(res_typ.dimensions))
        if len(set_typ) > 1 or len(set_dimen) > 1 or len(set_ele_typ) > 1:
            return IllegalArrayLiteral(ast)
        else:
            typ = res_typ
            if typ is None:
                return AutoType()
            for x in expr_auto:
                self.infer_type(x, typ, context)
            if isinstance(typ, ArrayType):
                return ArrayType([len(ast.explist)] + typ.dimensions, typ.typ)   
            else:     
                return ArrayType([len(ast.explist)], typ)

    def visitArrayLit(self, ast, context):
        res = self.visitNotThrowArrayLit(ast, context)
        if isinstance(res, IllegalArrayLiteral):
            raise res
        return res

    def visitBinExpr(self, ast, context):
        l_type = self.visit(ast.left, context)
        r_type = self.visit(ast.right, context)

        if isinstance(l_type, AutoType) or isinstance(r_type, AutoType):
            if type(l_type) == type(r_type):
                return AutoType()
            else:
                if isinstance(l_type, AutoType):
                    l_type = self.infer_type(ast.left, r_type, context)
                else: #r_type: auto
                    r_type = self.infer_type(ast.right, l_type, context)
        eval_type = None
        for op_group in StaticChecker.bi_dict.keys():
            if ast.op in op_group:
                sub_dict = StaticChecker.bi_dict[op_group]
                for input_types in sub_dict.keys():
                    if frozenset([type(l_type), type(r_type)]) == input_types:
                        eval_type = sub_dict[input_types]()
                        break
                break
        if eval_type is None:
            raise TypeMismatchInExpression(ast)
        return eval_type

    def visitUnExpr(self, ast, context):
        typ_obj = self.visit(ast.val, context)
        op_dict = {'!': {BooleanType}, '-': {IntegerType, FloatType}}
        if ast.op == '!' and isinstance(typ_obj, AutoType):
            self.infer_type(ast.val, BooleanType(), context)
            typ_obj = BooleanType()
        if type(typ_obj) != AutoType and type(typ_obj) not in op_dict[ast.op]:
            raise TypeMismatchInExpression(ast)
        return typ_obj

    def visitId(self, ast, context):
        sym = self.find_sym(ast.name, context)
        if (sym is None) or ((sym is not None) and isinstance(sym.value, FuncDecl)):
            raise Undeclared(Identifier(), ast.name)
        return sym.mtype

    def visitArrayCell(self, ast, context):
        arr = self.find_sym(ast.name, context)
        if arr is None:
            raise Undeclared(Identifier(), ast.name)
        elif not isinstance(arr.mtype, ArrayType):
            raise TypeMismatchInExpression(ast)
        for expr in ast.cell:
            self.check_match(context, expr, IntegerType(), ast)
        if len(ast.cell) > len(arr.mtype.dimensions): 
            raise TypeMismatchInExpression(ast)
        elif len(ast.cell) == len(arr.mtype.dimensions): 
            return arr.mtype.typ
        else: 
            return ArrayType(arr.mtype.dimensions[len(ast.cell):], arr.mtype.typ)

    def visitAssignStmt(self, ast, context):
        result = self.check_assign_typ(ast.lhs, ast.rhs, context)
        if result is None:
            raise TypeMismatchInStatement(ast)

    def visitBlockStmt(self, ast, context):
        func_owner = self.lookup("function", context[0], lambda x: x.name)
        func_owner2 = self.find_sym("function", context)
        body = ast.body
        #temp node for find function: 3rd attr  is ast
        if func_owner and func_owner.value.inherit:
            self.check_first_stmt(ast, func_owner.value, context)
            body = ast.body[1:]
        #func_owner2.mtype: not_end_check_ret
        for stmt in body:
            if isinstance(stmt, ReturnStmt) \
                    and not self.lookup("return", context[0], lambda x: x.name) \
                    and not func_owner2.mtype:
                self.visitReturnStmtV2(stmt, context)
                context[0].append(Symbol("return", None, None))
                if func_owner:
                    func_owner2.mtype = True    
            elif isinstance(stmt, BlockStmt):
                self.visit(stmt, [[]] + context)
            else:
                self.visit(stmt, context)
                
    def visitReturnStmtV2(self, ast, context):
        func_sym = self.find_sym("function", context)
        if not ast.expr:
            res = self.check_assign_typ(func_sym.value.return_type, VoidType(), context, is_return = True)
        else:
            res = self.check_assign_typ(func_sym.value.return_type, ast.expr, context, is_return = True)
        if res is None:
            raise TypeMismatchInStatement(ast)
        else:
            if isinstance(res[0], AutoType) and not isinstance(res[1], AutoType):
                self.set_ret_type(func_sym.value.name, res[1], context)
            elif isinstance(res[1], AutoType):
                self.infer_type(ast.expr, res[0], context)
                
        
    def visitReturnStmt(self, ast, context):
        return

    def visitIfStmt(self, ast, context):
        self.check_match(context, ast.cond, BooleanType(), ast)
        self.visit(self.convertStmtToBlock(ast.tstmt), [[]] + context)
        self.visit(self.convertStmtToBlock(ast.fstmt), [[]] + context) if ast.fstmt else None

    def visitForStmt(self, ast, context):
        self.check_match(context, ast.init.lhs, IntegerType(), ast)
        self.check_match(context, ast.init.rhs, IntegerType(), ast)
        self.check_match(context, ast.cond, BooleanType(), ast)
        self.check_match(context, ast.upd, IntegerType(), ast)
        self.visit(self.convertStmtToBlock(ast.stmt), [[Symbol("for", None, None)]] + context)

    def visitWhileStmt(self, ast, context):
        self.check_match(context, ast.cond, BooleanType(), ast)
        self.visit(self.convertStmtToBlock(ast.stmt), [[Symbol("for", None, None)]] + context)

    def visitDoWhileStmt(self, ast, context):
        self.check_match(context, ast.cond, BooleanType(), ast)
        self.visit(self.convertStmtToBlock(ast.stmt), [[Symbol("for", None, None)]] + context)

    def visitBreakStmt(self, ast, context):
        if not self.find_sym("for", context):
            raise MustInLoop(ast)

    def visitContinueStmt(self, ast, context):
        if not self.find_sym("for", context):
            raise MustInLoop(ast)



    def visitVarDecl(self, ast, context):
        var_sym = self.lookup(ast.name, context[0] + StaticChecker.global_envi, lambda x: x.name)
        ret_typ = ast.typ
        if var_sym:
            raise Redeclared(Variable(), ast.name)
        ######################
        if isinstance(ast.typ, AutoType):
            if ast.init is None:
                raise Invalid(Variable(), ast.name)
            else:
                
                context[0] = [(Symbol(ast.name, ast.typ, ast.init))] + context[0]
                l_typ, r_typ = self.check_assign_typ(ast.typ, ast.init, context, is_init = True)
                ast.typ = r_typ
                context[0][0].mtype = r_typ     
                return
        ######################
        elif isinstance(ast.typ, ArrayType):
            if ast.init is not None and isinstance(ast.init, ArrayLit):
                right_typ = self.visit(ast.init, context)
                if not self.compareArrayType(ast.typ, right_typ):
                    raise TypeMismatchInVarDecl(ast)
        context[0] = [(Symbol(ast.name, ret_typ, ast.init))] + context[0]
        if ast.init:
            res = self.check_assign_typ(Id(ast.name), ast.init, context, is_init = True)
            if res is None:
                raise TypeMismatchInVarDecl(ast)
        
    def compareArrayType(self, left_typ, right_typ):

        if tuple(right_typ.dimensions) != tuple(left_typ.dimensions):
            return None
        
        elif type(right_typ.typ) != type(left_typ.typ):
            return None
        
        else: 
            
            return True

    def visitDadParamDecls(self, child_func, dad_func, context):
        cur_param_list = []
        if self.lookup(dad_func.name, StaticChecker.global_envi, lambda x: x.name):
            return
        for x in dad_func.value.params:
            temp_sym = Symbol(x.name, x.typ, x, dad_func)
            if x.inherit:
                res1 = self.lookup(x.name, cur_param_list, lambda x: x.name)
                if res1:
                    raise Redeclared(Parameter(), x.name)
                cur_param_list.append(temp_sym)
        cur_param_list = []
        for x in dad_func.value.params:
            temp_sym = Symbol(x.name, x.typ, x, dad_func)
            if x.inherit:
                res2 = self.lookup(x.name, child_func.value.params, lambda x: x.name)
                if res2:
                    raise Invalid(Parameter(), x.name)
                cur_param_list.append(temp_sym)
                context[0] = [temp_sym] + context[0]
                    
    def visitParamDecl(self, ast, context):
        func_ast = self.lookup("function", context[0], lambda x: x.name).value
        func_sym = self.lookup(func_ast.name, self.list_func, lambda x: x.name)
        param_sym = self.lookup(ast.name, context[0] + StaticChecker.global_envi, lambda x: x.name)
        if param_sym:
            raise Redeclared(Parameter(), ast.name)    
        # invalid_para_flag = False
        # if func_ast.inherit:
        #     parent_sym = self.lookup(func_ast.inherit, self.list_func, lambda x: x.name)
        #     if param_sym and param_sym.name in [x.name for x in parent_sym.value.params if x.inherit]:
        #         invalid_para_flag = True 
        #         if ast.inherit:
        #             Redeclared(Parameter(), ast.name)
        # if param_sym and invalid_para_flag:
        #     raise Invalid(Parameter(), ast.name)
        context[0].append(Symbol(ast.name, ast.typ, ast, func_sym))

    def visitFloatType(self, ast, context): return FloatType()
    def visitIntegerType(self, ast, context): return IntegerType()
    def visitBooleanType(self, ast, context): return BooleanType()
    def visitVoidType(self, ast, context): return VoidType()
    def visitStringType(self, ast, context): return StringType()
    def visitAutoType(self, ast, context): return AutoType()
    def visitArrayType(self, ast, context): return ast
    def visitIntegerLit(self, ast, context): return IntegerType()
    def visitFloatLit(self, ast, context): return FloatType()
    def visitStringLit(self, ast, context): return StringType()
    def visitBooleanLit(self, ast, context): return BooleanType()

    def convertStmtToBlock(self, ast):
        if isinstance(ast, BlockStmt):
            return ast
        else:
            return BlockStmt([ast])
        
    def check_match(self, context, expr, typ, ast=None):
        typ_expr = self.visit(expr, context)
        if isinstance(typ_expr, AutoType):
            typ_expr = self.infer_type(expr, typ, context)
        if type(typ_expr) != type(typ):
            if isinstance(ast, Expr):
                raise TypeMismatchInExpression(ast)
            elif isinstance(ast, Stmt):
                raise TypeMismatchInStatement(ast)
        return typ

    def find_sym(self, name, env):
        #find sym in 2 dimension list
        for sub_env in env:
            for sym in sub_env:
                if sym.name == name:
                    return sym
        return None

    def set_ret_type(self, func_name, typ_obj, context = None):
        for func in self.list_func:
            if func.name == func_name:
                typ = self.visit(typ_obj, None)
                func.value.return_type = typ
                func.mtype.rettype = typ
                return func.mtype.rettype
    def set_type(self, var_name, typ_obj, context):
        for lst in context:
            for x in lst:
                if x.name == var_name:
                    typ = self.visit(typ_obj, None)
                    if isinstance(x.value, ParamDecl): #param only
                        for i, param in enumerate(x.func_sym.value.params):
                            if param.name == var_name:
                                x.func_sym.value.params[i].typ = typ
                                x.func_sym.mtype.partype[i] = typ
                    x.mtype = typ
                    return x.mtype

    def find_func_sym(self, name, context):
        if name in ["preventDefault", "super"]:
            return self.lookup(name, context[0], lambda x: x.name)
        else:
        
            return self.lookup(name, self.list_func, lambda x: x.name)
        
    def check_param_list(self, list_type_param, list_expr, context, func_name = None):

        list_pair_res = []
        zip_lst = zip(list_expr, list_type_param)
        if func_name and func_name in ["super", "preventDefault"]:
            if len(list_expr) < len(list_type_param):
                raise TypeMismatchInExpression()
            elif len(list_expr) > len(list_type_param):
                raise TypeMismatchInExpression(list_expr[len(list_type_param)])
        elif len(list_expr) != len(list_type_param):
            return None
        for expr, type_param in zip_lst:
            typ = self.check_assign_typ(type_param, expr, context, is_param = True)
            if not typ:
                if func_name and func_name in ["super", "preventDefault"]:
                    raise TypeMismatchInExpression(expr)
                return None
            list_pair_res.append(typ)
        return list_pair_res

    def check_assign_typ(self, lhs, rhs, context, is_param = False, is_init = False, is_return = False):
        #lhs: type_obj, rhs: expr
        l_typ = self.visit(lhs, context)
        r_typ = self.visit(rhs, context)

        if type(l_typ) == VoidType:
            return None
        if type(l_typ) in [ArrayType]:
            if is_param or is_init or is_return:
                if isinstance(r_typ, ArrayType):
                    if self.compareArrayType(l_typ, r_typ):
                        return l_typ, r_typ
                    else: 
                        return None
                    
        if isinstance(l_typ, AutoType):
            if isinstance(lhs, Id) and type(l_typ) != type(r_typ):
                l_typ = self.infer_type(lhs, r_typ, context)
            return l_typ, r_typ
        elif isinstance(r_typ, AutoType) :
            if type(l_typ) != type(r_typ):
                r_typ = self.infer_type(rhs, l_typ, context)
        elif type(l_typ) != type(r_typ):
            if isinstance(l_typ, FloatType) and isinstance(r_typ, IntegerType):
                return FloatType(), IntegerType()
            else:
                return None
        return l_typ, r_typ

    def check_first_stmt(self, ast_block, func_ast, context):
        
        parent_sym = self.lookup(func_ast.inherit, self.list_func, lambda x: x.name)

        first = ast_block.body[0] if len(ast_block.body) != 0 else None 
        if len(parent_sym.mtype.partype) != 0:
            if len(ast_block.body) == 0:
                raise InvalidStatementInFunction(func_ast.name)
            if not ((isinstance(first, CallStmt)) and (first.name in ["preventDefault", "super"])):
                raise InvalidStatementInFunction(func_ast.name)
        else:
            if len(ast_block.body) == 0:
                return True
            elif not isinstance(first, CallStmt):
                return True
        
        if first.name == "preventDefault" and self.check_param_list(first.args, [], context, "preventDefault"):
            return True
        if first.name == "super" and self.check_param_list(parent_sym.mtype.partype, first.args, context, "super"):
            self.visitCallStmt(CallStmt(func_ast.inherit, first.args), context)
            if parent_sym.value is None:
                return True
            for x in parent_sym.value.params:
                self.set_type(x.name, x.typ, context)
            return True

    def infer_type(self, ast, typ_obj, context):
        if isinstance(ast, BinExpr):
            self.infer_type(ast.left, typ_obj, context)
            self.infer_type(ast.right, typ_obj, context)
        elif isinstance(ast, UnExpr):
            self.infer_type(ast.val, typ_obj, context)
        elif isinstance(ast, Id):
            self.set_type(ast.name, typ_obj, context)
        elif isinstance(ast, FuncCall):
            self.set_ret_type(ast.name, typ_obj, context)
        elif isinstance(ast, ArrayLit):
            for x in ast.explist:
                self.infer_type(x, typ_obj, context)
        return typ_obj

class CodeGenerator(Visitor, Utils):
    def __init__(self):
        self.libName = "io"

    def init(self):
        global_envi = [
            Symbol("readInteger", MType([], IntegerType())),
            Symbol("printInteger", MType([IntegerType()], VoidType()),CName(self.libName)),
            Symbol("readFloat", MType([], FloatType()),CName(self.libName)),
            Symbol("printFloat", MType([FloatType()], VoidType()),CName(self.libName)),
            Symbol("readBoolean", MType([], BooleanType()),CName(self.libName)),
            Symbol("printBoolean", MType([BooleanType()], VoidType()),CName(self.libName)),            
            Symbol("printString", MType([StringType()], VoidType()),CName(self.libName)),
            Symbol("readString", MType([], StringType()),CName(self.libName))
            # Symbol("preventDefault", MType([], VoidType()),CName(self.libName)),
            # Symbol("super", MType([], VoidType))
        ]
        return global_envi

    def gen(self, ast, dir_):
        #ast: AST
        #dir_: String

        gl = self.init()
        new_ast = StaticChecker(ast).check()
        gc = CodeGenVisitor(new_ast, gl, dir_)
        gc.visit(ast, None)

# class StringType(Type):
    
#     def __str__(self):
#         return "StringType"

#     def accept(self, v, param):
#         return None

class ArrayPointerType(Type):
    def __init__(self, ctype):
        #cname: String
        self.eleType = ctype

    def __str__(self):
        return "ArrayPointerType({0})".format(str(self.eleType))

    def accept(self, v, param):
        return None
    
class ClassType(Type):
    def __init__(self,cname):
        self.cname = cname
    def __str__(self):
        return "Class({0})".format(str(self.cname))
    def accept(self, v, param):
        return None
        
class SubBody():
    def __init__(self, frame, sym):
        self.frame = frame
        self.sym = sym

class Access():
    def __init__(self, frame, sym, isLeft, isFirst = False):
        self.frame = frame
        self.sym = sym
        self.isLeft = isLeft
        self.isFirst = isFirst

class Val(ABC):
    pass

class Index(Val):
    def __init__(self, value):
        self.value = value

class CName(Val):
    def __init__(self, value):
        self.value = value
        
class CodeGenVisitor(Utils, Visitor):
    def __init__(self, astTree, env, dir_):
        self.astTree = astTree
        self.env = env #global
        self.className = "MT22Class"
        self.path = dir_
        self.emit = Emitter(self.path + "/" + self.className + ".j")
        self.op_dict = {
            ('>', '<', '>=', '<=', '==', '!='): self.emit.emitREOP,
            ('&&',): self.emit.emitANDOP,
            ('||',): self.emit.emitOROP,
            ('+', '-'): self.emit.emitADDOP,
            ('*', '/'): self.emit.emitMULOP,
            ('%',): self.emit.emitMOD
        } 
        
    def visitProgram(self, ast, c):
        #ast: Program
        #c: None
        #return list_sym
        self.emit.printout(self.emit.emitPROLOG(self.className, "java.lang.Object"))
        self.env += [Symbol(f.name, \
                            MType([param.typ for param in f.params], f.return_type), \
                            CName("MT22Class")) \
                    for f in ast.decls if type(f) == FuncDecl]
        self.env += [Symbol(x.name,
                            x.typ, \
                            CName("MT22Class")) \
                    for x in ast.decls if type(x) == VarDecl]
        env = SubBody(None, self.env)
        field_access = Access(Frame("MT22Class", None), env.sym, True, True)
        
        for x in ast.decls:
            if type(x) == VarDecl:
                env = self.visit(x, field_access)
        main_ast = [x for x in ast.decls if type(x) == FuncDecl and x.name == "main"][0]
        env = self.visit(main_ast, env)
        for x in ast.decls:
            if type(x) != VarDecl and x.name != "main":
                env = self.visit(x, env)
        # generate default constructor
        gen_func = FuncDecl("<init>", None, list(), None, BlockStmt( list()))
        # gen_func.body.body = [(AssignStmt(Id(x.name), x.init)) for x in ast.decls if type(x) is VarDecl]

        self.genMETHOD(gen_func, self.env, Frame("<init>", VoidType))
        self.emit.emitEPILOG()
        return c

    def genMETHOD(self, consdecl, sym, frame):
        
        #consdecl: FuncDecl
        #o: list_symbol
        #frame: Frame

        isInit = consdecl.return_type is None
        isMain = consdecl.name == "main" and len(consdecl.params) == 0 and type(consdecl.return_type) is VoidType
        returnType = VoidType() if isInit else consdecl.return_type
        methodName = "<init>" if isInit else consdecl.name

        if isInit:
            intype = []
        else:
            func_sym = self.lookup(consdecl.name, sym, lambda x: x.name)
            intype = [ArrayPointerType(StringType())] if isMain else func_sym.mtype.partype 
        mtype = MType(intype, returnType)
        self.emit.printout(self.emit.emitMETHOD(methodName, mtype, not isInit, frame))
        frame.enterScope(True)

        # Generate code for parameter declarations
        if isInit:
            self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), "this", ClassType(self.className), frame.getStartLabel(), frame.getEndLabel(), frame))
        if isMain:
            self.emit.printout(self.emit.emitVAR(frame.getNewIndex(), "args", ArrayPointerType(StringType()), frame.getStartLabel(), frame.getEndLabel(), frame))
            for x in self.astTree.decls:
                if type(x) is VarDecl:
                    consdecl.body.body = [AssignStmt(Id(x.name), x.init)] + consdecl.body.body
                    
        body = consdecl.body
        self.emit.printout(self.emit.emitLABEL(frame.getStartLabel(), frame))

        # Generate code for statements
        if isInit:
            self.emit.printout(self.emit.emitREADVAR("this", ClassType(self.className), 0, frame))
            self.emit.printout(self.emit.emitINVOKESPECIAL(frame))
        
        env = SubBody(frame, sym)

        for x in consdecl.params:
            env = self.visit(VarDecl(x.name, x.typ), env)   
        
        for x in body.body:
            if isinstance(x, VarDecl):
                env = self.visit(x, env)
            else:
                self.visit(x, env)
        
                
        self.emit.printout(self.emit.emitLABEL(frame.getEndLabel(), frame))
        if type(returnType) is not None:
            for x in consdecl.params:
                if x.out:
                    self.visitId(Id(x.name), Access(frame, sym, False, False))
                    
            self.emit.printout(self.emit.emitRETURN(returnType, frame))
        self.emit.printout(self.emit.emitENDMETHOD(frame))
        frame.exitScope();

    def visitFuncDecl(self, ast, o):
        subastt = o
        frame = Frame(ast.name, ast.return_type)
        if ast.inherit:
            if ast.body.body[0].name == "super":
                ast.body.body[0].name = ast.inherit
            parent_ast = [x for x in self.astTree.decls if type(x) == FuncDecl and x.name == ast.inherit][0]
            ast.body.body = [VarDecl(x.name, x.typ) for x in parent_ast.params if x.inherit] + ast.body.body
            # ast.params += [x for x in parent_ast.params if x.inherit]
        self.genMETHOD(ast, subastt.sym, frame)
        # return SubBody(None, [Symbol(ast.name, MType(list(), ast.return_type), CName(self.className))] + subastt.sym)
        # o.sym += [Symbol(ast.name, MType(list(), ast.return_type), CName(self.className))]
        return SubBody(None, subastt.sym)
    
    def visitCallStmt(self, ast, o):
        if ast.name == "preventDefault":
            return "", VoidType()
                
        astt = o
        frame = astt.frame
        nenv = astt.sym
        sym = self.lookup(ast.name, self.env, lambda x: x.name)
        cname = sym.value.value
        ctype = sym.mtype
        partype = ctype.partype
        in_ = ("", list())
        count = 0
        for x in ast.args:
            str1, typ1 = self.visit(x, Access(frame, nenv, False, True))
            if {type(partype[count]), type(typ1)} == {IntegerType, FloatType}:
                str1 += self.emit.emitI2F(o.frame)
            in_ = (in_[0] + str1, in_[1].append(typ1))
            count += 1
        self.emit.printout(in_[0])
        self.emit.printout(self.emit.emitINVOKESTATIC(cname + "/" + ast.name, ctype, frame))
        func_ast = [x for x in self.astTree.decls if type(x) == FuncDecl and x.name == ast.name]
        if len(func_ast) > 0:
            func_ast = func_ast[0]
            for i, x in reversed(list(enumerate(ast.args))):
                if func_ast.params[i].out and type(x) is Id:
                    self.visitId(Id(x.name), Access(frame, nenv, True, False))        
        return "", sym.mtype.rettype
        
    def visitFuncCall(self, ast, o):
        #have printed in call statement\
        res = self.visit(CallStmt(ast.name, ast.args), o)
        return res
        
    
    def visitIntegerLit(self, ast, o):
        astt = o
        frame = astt.frame
        return self.emit.emitPUSHICONST(ast.val, frame), IntegerType()
    
    def visitFloatLit(self, ast, o):
        return self.emit.emitPUSHFCONST(str(ast.val), o.frame), FloatType()
    
    def visitBooleanLit(self, ast, o):
        return self.emit.emitPUSHICONST(int(ast.val), o.frame), BooleanType() 
    
    def visitBinExpr(self, ast, o):
        #only for float, int, boolean
        
        jsmc1, typ1 = self.visit(ast.left, o)
        jsmc2, typ2 = self.visit(ast.right, o)
        if {type(typ1), type(typ2)} == {IntegerType, FloatType}:
            
            if type(typ1) == IntegerType:
                jsmc1 += self.emit.emitI2F(o.frame)
                typ1 = FloatType()
            else:
                jsmc2 += self.emit.emitI2F(o.frame)
                typ2 = FloatType()
        typ = typ1
        for group in self.op_dict:
            if ast.op in group:
                opr = self.op_dict[group]
                if len(group) == 1:
                    ret_typ = IntegerType() if '%' in group else typ
                    return jsmc1 + jsmc2 + opr(o.frame), ret_typ
                else:    
                    ret_typ = BooleanType() if '>' in group else typ
                    return jsmc1 + jsmc2 + opr(ast.op, typ, o.frame), ret_typ

    def visitUnExpr(self, ast, o):
        jsmc, typ = self.visit(ast.val, o)
        if ast.op == '-':
            return jsmc + self.emit.emitNEGOP(typ, o.frame), typ
        else:
            return jsmc + self.emit.emitNOT(typ, o.frame), BooleanType()
        
    def visitVarDecl(self, ast, o):
        #use result for update enviroment 
        if type(o) != SubBody:
            jsm = self.emit.emitATTRIBUTE(ast.name, ast.typ, None)
            self.emit.printout(jsm)
            result = SubBody(o.frame, [Symbol(ast.name, ast.typ, CName("MT22Class"))] + o.sym)
            #init in constructor
            # if (ast.init):
            #     self.visit(AssignStmt(Id(ast.name), ast.init), o)
            return result
        else:
            jsm = self.emit.emitVAR(o.frame.getCurrIndex(), ast.name, ast.typ, o.frame.getStartLabel(), o.frame.getEndLabel(), o.frame)
            self.emit.printout(jsm)
            result = SubBody(o.frame, [Symbol(ast.name, ast.typ, Index(o.frame.getNewIndex()))] + o.sym)
            if (ast.init):
                self.visit(AssignStmt(Id(ast.name), ast.init), result)
            return result

        
    def visitId(self, ast, o):
        for obj in o.sym:
            if obj.name == ast.name:
                if o.isLeft == False:
                    if isinstance(obj.value.value, int):
                        return self.emit.emitREADVAR(obj.name, obj.mtype, obj.value.value, o.frame), obj.mtype
                    return self.emit.emitGETSTATIC(obj.value.value + '/' + obj.name, obj.mtype, o.frame), obj.mtype
                else:
                    if isinstance(obj.value.value, int):
                        return self.emit.emitWRITEVAR(obj.name, obj.mtype, obj.value.value, o.frame), obj.mtype
                    return self.emit.emitPUTSTATIC(obj.value.value + '/' + obj.name, obj.mtype, o.frame), obj.mtype
                
                
    def visitAssignStmt(self, ast, o):
       
        left_access = Access(o.frame, o.sym, True)
        right_access = Access(o.frame, o.sym, False)

        right_jsm, typr = self.visit(ast.rhs, right_access)
        left_jsm, typl = self.visit(ast.lhs, left_access)

        if (type(typl), type(typr))  == (FloatType, IntegerType):
            right_jsm +=  self.emit.emitI2F(o.frame)
        return self.emit.printout(right_jsm + left_jsm)
    
    def visitIfStmt(self,ast,o):
        expr_jsm, typ = self.visit(ast.cond, Access(o.frame, o.sym, False))
        if not ast.fstmt:
            label_exit = o.frame.getNewLabel()
            self.emit.printout(expr_jsm)
            self.emit.printout(self.emit.emitIFFALSE(label_exit, o.frame))
            self.visit(ast.tstmt, o)
            self.emit.printout(self.emit.emitLABEL(label_exit, o.frame))
        else:
            label_else = o.frame.getNewLabel()
            label_exit = o.frame.getNewLabel()
            self.emit.printout(expr_jsm)
            self.emit.printout(self.emit.emitIFFALSE(label_else, o.frame))
            self.visit(ast.tstmt, o)
            self.emit.printout(self.emit.emitGOTO(label_exit, o.frame))
            self.emit.printout(self.emit.emitLABEL(label_else, o.frame))
            self.visit(ast.fstmt, o)
            self.emit.printout(self.emit.emitLABEL(label_exit, o.frame))
    
    def visitWhileStmt(self,ast,o):
        o.frame.enterLoop()
        label_exit = o.frame.getBreakLabel()
        cont_label = o.frame.getContinueLabel()
        self.emit.printout(self.emit.emitLABEL(cont_label, o.frame))
        expr_jsm, typ = self.visit(ast.cond, Access(o.frame, o.sym, False))
        self.emit.printout(expr_jsm)
        self.emit.printout(self.emit.emitIFFALSE(label_exit, o.frame))
        self.visit(ast.stmt, o)
        self.emit.printout(self.emit.emitGOTO(cont_label, o.frame))
        self.emit.printout(self.emit.emitLABEL(label_exit, o.frame))
        o.frame.exitLoop()
    
    def visitDoWhileStmt(self,ast,o):
        self.visit(ast.stmt, o)
        while_ast = WhileStmt(ast.cond, ast.stmt)
        self.visit(while_ast, o)
        
    def visitForStmt(self, ast, o):
        self.visit(ast.init, o)
        upd_ast = AssignStmt(ast.init.lhs, ast.upd)
        if not isinstance(ast.stmt, BlockStmt):
            ast.stmt = BlockStmt([ast.stmt])
        if_ast = IfStmt(ast.cond, ast.stmt, None)
        if_not_ast = IfStmt(ast.cond, ast.stmt, BreakStmt())
        while_ast = WhileStmt(BooleanLit(True), BlockStmt([upd_ast, if_not_ast]))
        
        self.visit(if_ast, o)
        self.visit(while_ast, o)

    
    def visitBreakStmt(self, ast, o):
        self.emit.printout(self.emit.emitGOTO(o.frame.getBreakLabel(), o.frame))
    
    def visitConinueStmt(self, ast, o):
        self.emit.printout(self.emit.emitGOTO(o.frame.getContinueLabel(), o.frame))
    
    def visitReturnStmt(self, ast, o):
        ret_type = o.frame.returnType
        if ast.expr:
            expr_jsm, typ_expr = self.visit(ast.expr, Access(o.frame, o.sym, False, True))
            if (type(ret_type), type(typ_expr)) == {FloatType, IntegerType}:
                expr_jsm += self.emit.emitI2F(o.frame)
            self.emit.printout(expr_jsm)
        self.emit.printout(self.emit.emitGOTO(o.frame.getEndLabel(), o.frame))
    
    def visitBlockStmt(self, ast, o):
        #not for function
        o.frame.enterScope(False)
        self.emit.printout(self.emit.emitLABEL(o.frame.getStartLabel(), o.frame))
        env = o
        for x in ast.body:
            if isinstance(x, VarDecl):
                env = self.visit(x, env)
            else:
                self.visit(x, env)
        self.emit.printout(self.emit.emitLABEL(o.frame.getEndLabel(), o.frame))
        o.frame.exitScope()
        return env

    
    def visitArrayCell(self, ast, o):
        
        arr_jsm, arr_typ = self.visit(Id(ast.name), Access(o.frame, o.sym, True, True))
        idx_jsm, idx_typ = self.visit(ast.cell[0], Access(o.frame, o.sym, False, True))
        
        if o.isLeft:
            return [arr_jsm + idx_jsm, self.emit.emitASTORE(arr_typ.typ, o.frame)], arr_typ.typ
        else:
            return arr_jsm + idx_jsm + self.emit.emitALOAD(arr_typ.typ, o.frame), arr_typ.typ
    
    def visitArrayLit(self, ast, o):
        length_arr = len(ast.explist)
        typ_arr = self.visit(ast.explist[0], Access(o.frame, o.sym, False, True))[1]
        arr_jsm = self.emit.emitPUSHICONST(length_arr, o.frame)
        arr_jsm += self.emit.emitNEWARRAY(typ_arr, o.frame)
        for i in range(length_arr):
            arr_jsm += self.emit.emitDUP(o.frame)
            arr_jsm += self.emit.emitPUSHICONST(i, o.frame)
            arr_jsm += self.visit(ast.explist[i], Access(o.frame, o.sym, False, True))[0]
            arr_jsm += self.emit.emitASTORE(typ_arr, o.frame)
        return arr_jsm, ArrayType(length_arr, typ_arr)
    