INDENT = "\t"
END = "\n"

class Reason:
    FOR_READ_FROM_MEM = 0
    FOR_LHS = 1
    FOR_TEMP_VALUE = 2

class TypeRegister:
    TEMP = 0
    VAR = 1
    PARAM = 2
    ARG = 3
    OTHER = 4

class RegisterDescriptor:
    nameDict = {0: "zero", 1: "at", 2: "v0", 3: "v1",
                4: "a0", 5: "a1", 6: "a2", 7: "a3",
                8: "t0", 9: "t1", 10: "t2", 11: "t3",
                12: "t4", 13: "t5", 14: "t6", 15: "t7",
                16: "s0", 17: "s1", 18: "s2", 19: "s3",
                20: "s4", 21: "s5", 22: "s6", 23: "s7",
                24: "t8", 25: "t9", 26: "k0", 27: "k1",
                28: "gp", 29: "sp", 30: "fp", 31: "ra"}

    def __init__(self, name, is_general_purpose = True, var = None, is_dirty = False):
        self.is_dirty = is_dirty
        self.var = var
        self.name = name
        self.is_general_purpose = is_general_purpose
        self.last_time_used = -1


class RegisterManager:
    def __init__(self, emitter):
        self.time = 0
        self.emitter = emitter
        self.regs = dict()
        self.regs["zero"] = RegisterDescriptor("$zero", False, None, False)
        self.regs["at"] = RegisterDescriptor("$at", False, None, False)
        self.regs["gp"] = RegisterDescriptor("$gp", False, None, False)
        self.regs["sp"] = RegisterDescriptor("$sp", False, None, False)
        self.regs["fp"] = RegisterDescriptor("$fp", False, None, False)
        self.regs["ra"] = RegisterDescriptor("$ra", False, None, False)
        for x in range(0, 2):
            self.regs["k" + str(x)] = RegisterDescriptor("$k" + str(x), False, None, False)
        for x in range(0, 2):
            self.regs["v" + str(x)] = RegisterDescriptor("$v" + str(x), False, None, False)
        for x in range(0, 4):
            self.regs["a" + str(x)] = RegisterDescriptor("$a" + str(x), False, None, False)

        for x in range(0, 10):
            self.regs["t" + str(x)] = RegisterDescriptor("$t" + str(x), True, None, False)
        
        for x in range(0, 8):
            self.regs["s" + str(x)] = RegisterDescriptor("$s" + str(x), True, None, False)

    def emit(self, code):
        self.emitter.emit(code)
    
    def findInParamRegister(self, var):
        for x in range(0, 4):
            reg = self.regs["a" + str(x)]
            if self.isSameReference(reg.var, var):
                return reg
        return None
    
    def getRegister(self, var = None, reason = None, avoid_reg1 = None, avoid_reg2 = None):
        reg = self.findInParamRegister(var)
        if reg is None:
            reg = self.findRegisterWithContents(var)
        if reg is None:
            reg = self.findRegisterWithContents(None)

            if not reg:
                reg = self.selectRegisterToRelease(avoid_reg1, avoid_reg2)
                self.releaseRegister(reg)
            reg.var = var
            if reason == Reason.FOR_READ_FROM_MEM:
                base_reg = self.regs['fp'] if (not var.is_global) else self.regs['gp']
                self.emit(INDENT + "lw " + reg.name + " " + str(var.offset) + '(' + base_reg.name + ')' + END)
                reg.is_dirty = False
                
        if reason == Reason.FOR_LHS:
            reg.is_dirty = True
        reg.last_time_used = self.time
        self.time += 1
        return reg
    
    def getRegisterForGetVar(self, location, avoid_reg1 = None, avoid_reg2 = None):
        return self.getRegister(location, Reason.FOR_READ_FROM_MEM, avoid_reg1, avoid_reg2)

    def getRegisterForUpdateVar(self, location, avoid_reg1 = None, avoid_reg2 = None):
        return self.getRegister(location, Reason.FOR_LHS, avoid_reg1, avoid_reg2)

    def getRegisterForTemp(self, location, avoid_reg1 = None, avoid_reg2 = None):
        return self.getRegister(location, Reason.FOR_TEMP_VALUE, avoid_reg1, avoid_reg2)

    def getRegisterForParam(self, param, index):
        reg = self.regs["a" + str(index)]
        reg.var = param
        return reg

    def isSameReference(self, ref1, ref2):
        return ref1 is ref2

    def findRegisterWithContents(self, var):
        for i in self.regs.keys():
            if self.regs[i].is_general_purpose and self.isSameReference(var, self.regs[i].var):
                return self.regs[i]
        return None

    def selectRegisterToRelease(self, avoid1, avoid2):
        min_time = None
        possible_reg = None
        for reg in self.regs.values():
            if reg is not avoid1 and reg is not avoid2 and reg.is_general_purpose:
                if not reg.is_dirty and reg.last_time_used < self.time - 2:
                    return reg
                else:
                    if not min_time: 
                        min_time = reg.last_time_used
                        possible_reg = reg
                    elif min_time > reg.last_time_used: 
                        min_time = reg.last_time_used
                        possible_reg = reg
        return possible_reg

    def releaseRegister(self, reg):
        var = reg.var
        if var and reg.is_dirty:
            base_reg = self.regs['fp'] if (not var.is_global) else self.regs['gp']
            self.emit(INDENT + "sw " + reg.name + ", " + str(var.offset) + "(" + base_reg.name + ")" + END)
        reg.is_dirty = False
        reg.var = None

    def releaseAllDirtyRegisters(self):

        for i in self.regs.keys():
            if self.regs[i].is_general_purpose and self.regs[i].is_dirty:
                self.releaseRegister(self.regs[i])

    def releaseForEndFunction(self):
        for reg in self.regs.values():
            if reg.is_general_purpose and reg.var:
                if reg.var.is_global:
                    self.releaseRegister(reg)
                else:
                    reg.var = None











