from AST import *
from Visitor import *
from Utils import *
from StaticError import *

class MType:
    def __init__(self, partype, rettype):
        self.partype = partype
        self.rettype = rettype


class Symbol:
    def __init__(self, name, mtype, value=None, func_sym = None):
        self.name = name
        self.mtype = mtype
        self.value = value
        self.func_sym = func_sym


class StaticChecker(Visitor, Utils):
    global_envi = [
        Symbol("getInt", MType([], IntegerType())),
        Symbol("putIntLn", MType([IntegerType()], VoidType())),
        Symbol("readInteger", MType([], IntegerType())),
        Symbol("printInteger", MType([IntegerType()], VoidType())),
        Symbol("readFloat", MType([], FloatType())),
        Symbol("printFloat", MType([FloatType()], VoidType())),
        Symbol("printString", MType([StringType()], VoidType())),
        Symbol("readString", MType([], StringType())),
        Symbol("readBoolean", MType([], BooleanType())),
        Symbol("printBoolean", MType([BooleanType()],VoidType())),
        Symbol("preventDefault", MType([], VoidType())),
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
        return ""

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
        if sym is None:
            raise Undeclared(Function(), ast.name)
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
        if sym is None:
            raise Undeclared(Function(), ast.name)
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
        if func_owner and func_owner.value.inherit:
            self.check_first_stmt(ast, func_owner.value, context)
            body = ast.body[1:]
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
        if isinstance(ast.typ, AutoType):
            if ast.init is None:
                raise Invalid(Variable(), ast.name)
            else:
                context[0] = [(Symbol(ast.name, ast.typ, ast.init))] + context[0]
                l_typ, r_typ = self.check_assign_typ(ast.typ, ast.init, context, is_init = True)
                context[0][0].mtype = r_typ     
                return
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

        