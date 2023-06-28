class TACInstruction:
    def __init__(self):
        pass

    def emit(self, emitter):
        pass
    
class LoadConstant(TACInstruction):
    def __init__(self, dst, val):
        self.dst = dst
        self.val = val

    def emit(self, emitter):
        emitter.emitLoadConstant(self.dst, self.val)
    
    def __str__(self):
        return "LoadConstant: " + self.dst.name + " " + str(self.val)

# class LoadIntConstant(TACInstruction):
#     def __init__(self, dst, val):
#         self.dst = dst
#         self.val = val

#     def emit(self, emitter):
#         emitter.emitLoadIntConstant(self.dst, self.val)

# class LoadIntConstant(TACInstruction):
#     def __init__(self, dst, val):
#         self.dst = dst
#         self.val = val

#     def emit(self, emitter):
#         emitter.emitLoadIntConstant(self.dst, self.val)

# class LoadFloatConstant(TACInstruction):
#     def __init__(self, dst, val):
#         self.dst = dst
#         self.val = val

#     def emit(self, emitter):
#         emitter.emitLoadIntConstant(self.dst, self.val)
        
# class LoadBoolConstant(TACInstruction):
#     def __init__(self, dst, val):
#         self.dst = dst
#         self.val = val

#     def emit(self, emitter):
#         emitter.emitLoadIntConstant(self.dst, self.val)
        
# class LoadArrayConstant(TACInstruction):
#     def __init__(self, dst, val):
#         self.dst = dst
#         self.val = val

#     def emit(self, emitter):
#         emitter.emitLoadIntConstant(self.dst, self.val)

class LoadStringConstant(TACInstruction):
    def __init__(self, dst, str_lit):
        self.dst = dst
        self.str_lit = str_lit

    def emit(self, emitter):
        emitter.emitLoadStringConstant(self.dst, self.str_lit)
        
    def __str__(self):
        return "LoadStringConstant: " + self.dst.name + " " + self.str_lit

    
class LoadLabel(TACInstruction):
    def __init__(self, dst, label):
        self.dst = dst
        self.label = label

    def emit(self, emitter):
        emitter.emitLoadLabel(self.dst, self.label)
    
    def __str__(self):
        return "LoadLabel: " + self.dst.name + " " + self.label.name

class Assign(TACInstruction):
    def __init__(self, dst, src):
        self.dst = dst
        self.src = src

    def emit(self, emitter):
        emitter.emitCopy(self.dst, self.src)
        
    def __str__(self):
        return "Assign: " + self.dst.name + " " + self.src.name


class Load(TACInstruction):
    def __init__(self, dst, src, offset):
        self.dst = dst
        self.src = src
        self.offset = offset

    def emit(self, emitter):
        emitter.emitLoad(self.dst, self.src, self.offset)
        
    def __str__(self):
        return "Load: " + self.dst.name + " " + self.src.name + " " + str(self.offset)
    

class Store(TACInstruction):
    def __init__(self, dst, src, offset):
        self.dst = dst
        self.src = src
        self.offset = offset

    def emit(self, emitter):
        emitter.emitStore(self.dst, self.src, self.offset)
        
    def __str__(self):
        return "Store: " + self.dst.name + " " + self.src.name + " " + str(self.offset)

class BinaryOp(TACInstruction):
    def __init__(self, code, dst, op1, op2):
        self.code = code
        self.dst = dst
        self.op1 = op1
        self.op2 = op2

    def emit(self, emitter):
        emitter.emitBinaryOp(self.code, self.dst, self.op1, self.op2)
        
    def __str__(self):
        return "BinaryOp: " + self.code + " " + self.dst.name + " " + self.op1.name + " " + self.op2.name

class Label(TACInstruction):
    def __init__(self, label):
        self.label = label

    def emit(self, emitter):
        emitter.emitLabel(self.label)
        
    def __str__(self):
        return "Label: " + self.label


class Goto(TACInstruction):
    def __init__(self, label):
        self.label = label
        
    def emit(self, emitter):
        emitter.emitGoto(self.label)
    
    def __str__(self):
        return "Goto: " + self.label

class IfZ(TACInstruction):
    def __init__(self, cond, label):
        self.cond = cond
        self.label = label

    def emit(self, emitter):
        emitter.emitIfJump(self.cond, self.label)
        
    def __str__(self):
        return "IfZ: " + self.cond.name + " " + self.label


class BeginFunc(TACInstruction):
    def __init__(self, frame_size):
        self.frame_size = frame_size

    def emit(self, emitter):
        emitter.emitBeginFunction(self.frame_size)

    def __str__(self):
        return "BeginFunc: " + str(self.frame_size)

class EndFunc(TACInstruction):
    def __init__(self):
        pass

    def emit(self, emitter):
        emitter.emitEndFunction()

    def __str__(self):
        return "EndFunc"
    

class Return(TACInstruction):
    def __init__(self, val):
        self.val = val

    def emit(self, emitter):
        emitter.emitReturn(self.val)
    
    def __str__(self):
        return "Return: " + self.val.name

class PushParam(TACInstruction):

    def __init__(self, param, index):
        self.param = param
        self.index = index

    def emit(self, emitter):
        emitter.emitParam(self.param, self.index)

    def __str__(self):
        return "PushParam: " + self.param.name + " " + str(self.index)

class PopParams(TACInstruction):
    def __init__(self, num_bytes):
        self.num_bytes = num_bytes

    def emit(self, emitter):
        emitter.emitPopStack(self.num_bytes)
        
    def __str__(self):
        return "PopParams: " + str(self.num_bytes)
 

class LCall(TACInstruction):
    def __init__(self, name, result):
        self.name = name
        self.result = result

    def emit(self, emitter):
        emitter.emitLCall(self.result, self.name)
        
    def __str__(self):
        res = "LCall: " + self.name + " "
        if self.result:
            res += self.result.name
        return res


