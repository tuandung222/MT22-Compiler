from RegisterManager import *
    
class MipsEmitter:

    def __init__(self):
        self.str_num = 1
        self.buff = []
        self.list_reg = []
        self.RM = RegisterManager(self)
                    
    def emit(self, instr):
        self.buff.append(instr)

    def writeFile(self, file_name):
        self.emitIOFunction()
        with open(file_name, "w") as file:
            file.write(''.join(self.buff))

    def emitGetResult(self, retval):
        reg = self.RM.getRegisterForTemp(retval)
        self.emit(INDENT + "move " + reg.name + ", $v0" + END)

    def emitCallInstr(self, dst, fn, isLabel):
        self.RM.releaseAllDirtyRegisters()
        if isLabel:
            self.emit(INDENT + "jal " + fn + END)
        else:
            self.emit(INDENT + "jalr " + fn + END)
        if dst is not None:
            reg = self.RM.getRegisterForTemp(dst)
            self.emit(INDENT + "move " + reg.name + ", $v0" + END)
            return reg

    def emitLoadConstant(self,dst, val):
        reg = self.RM.getRegisterForTemp(dst, None, None)
        self.emit(INDENT + "li " + reg.name + ", " + str(val) + END)

    def emitLoadStringConstant(self, dst, val):
        label = "str" + str(self.str_num)
        self.emit(".data" + END)
        self.emit(label + ".asciiz " + val + END);
        self.emit(".text" + END)
        self.emitLoadLabel(dst, label)

    def emitLoad(self, dst, src, offset):
        src_reg = self.RM.getRegisterForTemp(src)
        dst_reg = self.RM.getRegisterForTemp(dst, src_reg)
        self.emit(INDENT + "lw " + dst_reg.name + ", " + str(offset) + "(" + src_reg.name + ")" + END)

    def emitStore(self, dst, value, offset):
        right_reg = self.RM.getRegisterForTemp(value)
        left_reg = self.RM.getRegisterForUpdateVar(dst, right_reg)
        self.emit(INDENT + "sw " + right_reg.name + ", " + str(offset) + "(" + left_reg.name + ")" + END)

    def emitCopy(self, dst, src):
        src_reg = self.RM.getRegisterForTemp(src)
        dst_reg = self.RM.getRegisterForUpdateVar(dst, src_reg)
        self.emit(INDENT + "move " + dst_reg.name + ", " + src_reg.name + END)

    def emitBinaryOp(self, op, dst, op1, op2):
        op_dict = {
            "+": "add", 
            "-": "sub", 
            "*": "mul", 
            "/": "div", 
            "%": "rem",
            "<": "slt",
            ">": "sgt",
            "<=": "sle",
            ">=": "sge",
            "==": "seq",
            "!=": "sne",
            "&&": "and",
            "||": "or"
        }
        if op1 and '@' not in op1.name:
            op1_reg = self.RM.getRegisterForGetVar(op1)
        else: 
            op1_reg = self.RM.getRegisterForTemp(op1)
        
        if op2 and '@' not in op2.name: 
            op2_reg = self.RM.getRegisterForGetVar(op2, op1_reg)
        else:
            op2_reg = self.RM.getRegisterForTemp(op2, op1_reg)
            
        dst_reg = self.RM.getRegisterForTemp(dst, op1_reg, op2_reg)
        self.emit(INDENT + op_dict[op] + " " + dst_reg.name + ", " + op1_reg.name + ", " + op2_reg.name + END)

    def emitLabel(self, label):
        self.RM.releaseAllDirtyRegisters()
        self.emit(label + ":" + END)

    def emitGoto(self, label):
        self.RM.releaseAllDirtyRegisters()
        self.emit(INDENT + "j " + label + END)

    def emitIfJump(self, cond, label):
        self.RM.releaseAllDirtyRegisters()
        cond_reg = self.RM.getRegisterForTemp(cond)
        self.emit(INDENT + "beqz " + cond_reg.name + ", " + label + END)

    def emitGetParams(self, lst_params):
        for i in range(0, len(lst_params)):
            self.RM.getRegisterForParam(lst_params[i], i)

    def emitReturn(self, retval = None):
        if retval:
            reg = self.RM.getRegisterForTemp(retval)
            self.emit(INDENT + "move $v0, " + reg.name + END)
        self.RM.releaseForEndFunction()
        self.emit(INDENT + "move $sp, $fp" + END)
        self.emit(INDENT + "lw $ra, -4($fp)" + END)
        self.emit(INDENT + "lw $fp, 0($fp)" + END)
        self.emit(INDENT + "jr $ra" + END)
        return retval

    def emitBeginFunction(self, frame_size):
        self.emit(INDENT + "subu $sp, $sp, 8" + END)
        self.emit(INDENT + "sw $fp, 8($sp)" + END)
        self.emit(INDENT + "sw $ra, 4($sp)" + END)
        self.emit(INDENT + "addiu $fp, $sp, 8" + END)
        if frame_size > 0:
            self.emit(INDENT + "subu $sp, $sp, " + str(frame_size) + END)

    def emitPushStack(self, num_bytes):
        self.emit(INDENT + "subu $sp, $sp, " + str(num_bytes) + END)

    def emitEndFunction(self):
        self.emit(END)

    def emitParam(self, arg, param_index):
        if arg and '@' not in arg.name:
            reg = self.RM.getRegisterForGetVar(arg)
        else:
            reg = self.RM.getRegisterForTemp(arg)
        if (param_index >= 4):
            self.emit(INDENT + "subu $sp, $sp, 4" + END)
            self.emit(INDENT + "sw " + reg.name + ", 4($sp)" + END)
        else:
            self.emit(INDENT + "move $a" + str(param_index) +", " + reg.name + END)

    def emitLCall(self, result, label):
        self.emitCallInstr(result, label, True)

    def emitPopStack(self, num_bytes):
        if num_bytes > 0:
            self.emit(INDENT + "add $sp, $sp, " + str(num_bytes) + END)
        self.emit(END)

    def emitGlobalVar(self, name, value):
        self.emit(INDENT + ".data" + END)
        self.emit(str(name) + ':' + INDENT + ".word" + INDENT + str(value) + END)

    def emitPreamble(self):
        self.emit(INDENT + ".text" + END)
        self.emit(INDENT + ".globl main" + END)

    def emitPrintFunction(self, func_name):
        pass

    def emitIOFunction(self):
        for func_name in ["printInteger", "printString", "printBoolean", "printFloat"]:
            self.emitPrintFunction(func_name)