from Utils import Utils
from TACInstruction import *
from MIPSEmitter import *

class TACSymbol:
    def __init__(self, is_global, offset, name):
        self.is_global = is_global
        self.offset = offset
        self.name = name

    def __eq__(self, other):
        return self is other


class TACGenerator(Utils):
    def __init__(self, file_name):
        self.file_name = file_name
        self.temp = 0
        self.buffer = []
        self.next_temp_num = 0
        self.next_global_offset = 0
        self.next_label_num = 0
        self.cur_stack_size = 0
        self.emitter = MipsEmitter()
        self.break_label_stack = []
        self.continue_label_stack = []

    def writeFile(self):
        for x in self.buffer:
            print(x)
            x.emit(self.emitter)
        self.emitter.writeFile(self.file_name)

    def getTempVar(self):
        name = str("@t" + str(self.next_temp_num))
        self.next_temp_num += 1
        return TACSymbol(False, 0, name)

    def getNewLocationOnStack(self, name):
        #offset to first local = -8
        self.cur_stack_size += 1
        sym = TACSymbol(False, self.cur_stack_size * (-4) + (-8), name);
        # self.emitter.emitPushStack(4)
        return sym

    def getFunctionReturn(self):
        return self.emitter.emitGetResult(self.getTempVar())

    def getNewGlobalVar(self, name):
        res = TACSymbol(True, self.next_global_offset, name)
        self.next_global_offset += 4
        # self.emitter.emitGlobalVar(name, 0)
        return res

    def genLoadConstant(self, dst, val):
        self.buffer.append(LoadConstant(dst, val))

    def genPopAllStack(self):
        num_bytes = self.cur_stack_size * 4
        self.cur_stack_size = 0
        self.emitter.emitPopStack(num_bytes)

    def genIfZ(self, cond, label):
        self.buffer.append(IfZ(cond, label))

    def genGoto(self, label):
        self.buffer.append(Goto(label))

    def getNewLabel(self):
        res = self.next_label_num
        self.next_label_num += 1
        return 'L' + str(res)

    def genLabel(self, label):
        self.buffer.append(Label(label))

    def genReturn(self, expr):
        self.buffer.append(Return(expr))

    def genBeginFunc(self):
        res = BeginFunc(0)
        self.cur_stack_size = 0
        self.buffer.append(res)
        return res

    def genEndFunc(self):
        self.buffer.append(EndFunc())

    def genLCall(self, label, is_return):
        res = self.getTempVar() if is_return else None
        self.buffer.append(LCall(label, res))
        return res

    def genBinaryOp(self, op, op1, op2):
        res = self.getTempVar()
        self.buffer.append(BinaryOp(op, res, op1, op2))
        return res

    def genLoad(self, dst, src, offset):
        res = self.getTempVar()
        self.buffer.append(Load(res, src, offset))
        return res

    def genStore(self, dst, src, offset):
        self.buffer.append(Store(dst, src, offset))

    def genPushParam(self, param, index):
        self.buffer.append(PushParam(param, index))

    def genPopStack(self, num_bytes):
        if num_bytes > 0:
            self.buffer.append(PopParams(num_bytes))

    def genAssign(self, dst, src):
        self.buffer.append(Assign(dst, src))

    def genPreamble(self):
        self.emitter.emitPreamble()

    def genReceiveParams(self, params):
        self.emitter.emitGetParams(params)
        
    def createBreakLabel(self):
        res = self.getNewLabel()
        self.break_label_stack.append(res)
        return res
    
    def createContinueLabel(self):
        res = self.getNewLabel()
        self.continue_label_stack.append(res)
        return res
    
    def popBreakLabel(self):
        return self.break_label_stack.pop()
    
    def popContinueLabel(self):
        return self.continue_label_stack.pop()
    
    def getBreakLabel(self):
        return self.break_label_stack[-1]
    
    def getContinueLabel(self):
        return self.continue_label_stack[-1]
    
    def exitLoop(self):
        self.popBreakLabel()
        self.popContinueLabel()
        
    def genPushStack(self, num_bytes):
        self.emitter.emitPushStack(num_bytes)
        
    
    