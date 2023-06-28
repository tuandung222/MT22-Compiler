from Utils import *
from StaticError import *
import CodeGenerator as cgen
from MachineCode import JasminCode

from AST import *

class MType:
    def __init__(self, partype, rettype):
        self.partype = partype
        self.rettype = rettype
        
class Emitter():
    def __init__(self, filename):
        self.filename = filename
        self.buff = list()
        self.jvm = JasminCode()

    def emitNEWARRAY(self, in_, frame):
        #in_: Type
        #frame: Frame
        
        frame.push()
        if type(in_) is IntegerType:
            return self.jvm.emitNEWARRAY("int")
        elif type(in_) is FloatType:
            return self.jvm.emitNEWARRAY("float")
        elif type(in_) is BooleanType:
            return self.jvm.emitNEWARRAY("boolean")
        elif type(in_) is cgen.StringType:
            return self.jvm.emitANEWARRAY("java/lang/String")
        elif type(in_) is cgen.ClassType:
            return self.jvm.emitANEWARRAY(in_.cname)



    def getJVMType(self, inType):
        typeIn = type(inType)
        if typeIn is IntegerType:
            return "I"
        elif typeIn is FloatType:
            return "F"
        elif typeIn is BooleanType:
            return "Z"
        elif typeIn is cgen.StringType:
            return "Ljava/lang/String;"
        elif typeIn is VoidType:
            return "V"
        elif typeIn is ArrayType:
            return "[" + self.getJVMType(inType.typ)
        elif typeIn is cgen.ArrayPointerType:
            return "[" + self.getJVMType(inType.eleType)
        elif typeIn is MType:
            return "(" + "".join(list(map(lambda x: self.getJVMType(x), inType.partype))) + ")" + self.getJVMType(inType.rettype)
        elif typeIn is cgen.ClassType:
            return "L" + inType.cname + ";"

    def getFullType(inType):
        typeIn = type(inType)
        if typeIn is IntegerType:
            return "int"
        elif typeIn is cgen.StringType:
            return "java/lang/String"
        elif typeIn is VoidType:
            return "void"
        elif typeIn is FloatType:
            return "float"
        elif typeIn is BooleanType:
            return "boolean"

    def emitPUSHICONST(self, in_, frame):
        #in: Int or String
        #frame: Frame
        
        frame.push();
        if type(in_) is int:
            i = in_
            if i >= -1 and i <=5:
                return self.jvm.emitICONST(i)
            elif i >= -128 and i <= 127:
                return self.jvm.emitBIPUSH(i)
            elif i >= -32768 and i <= 32767:
                return self.jvm.emitSIPUSH(i)
        elif type(in_) is str:
            if in_ == "true":
                return self.emitPUSHICONST(1, frame)
            elif in_ == "false":
                return self.emitPUSHICONST(0, frame)
            else:
                return self.emitPUSHICONST(int(in_), frame)

    def emitPUSHFCONST(self, in_, frame):
        #in_: String
        #frame: Frame
        
        f = float(in_)
        frame.push()
        rst = "{0:.4f}".format(f)
        if rst == "0.0" or rst == "1.0" or rst == "2.0":
            return self.jvm.emitFCONST(rst)
        else:
            return self.jvm.emitLDC(in_)           

    ''' 
    *    generate code to push a constant onto the operand stack.
    *    @param in the lexeme of the constant
    *    @param typ the type of the constant
    '''
    def emitPUSHCONST(self, in_, typ, frame):
        #in_: String
        #typ: Type
        #frame: Frame
        
        if type(typ) is IntegerType:
            return self.emitPUSHICONST(in_, frame)
        elif type(typ) is FloatType:
            return self.emitPUSHFCONST(in_, frame)
        elif type(typ) is BooleanType:
            return self.emitPUSHICONST(in_, frame)
        elif type(typ) is StringType:
            frame.push()
            return self.jvm.emitLDC(in_)
        else:
            raise IllegalOperandException(in_)

    ##############################################################

    def emitALOAD(self, in_, frame):
        #in_: Type
        #frame: Frame
        #..., arrayref, index, value -> ...
        
        frame.pop()
        if type(in_) is IntegerType:
            return self.jvm.emitIALOAD()
        elif type(in_) is cgen.ArrayPointerType or type(in_) is cgen.ClassType or type(in_) is StringType:
            return self.jvm.emitAALOAD()
        else:
            raise IllegalOperandException(str(in_))

    def emitASTORE(self, in_, frame):
        #in_: Type
        #frame: Frame
        #..., arrayref, index, value -> ...
        
        frame.pop()
        frame.pop()
        frame.pop()
        if type(in_) is IntegerType:
            return self.jvm.emitIASTORE()
        elif type(in_) is FloatType:
            return self.jvm.emitFASTORE()
        elif type(in_) is BooleanType: 
            return self.jvm.emitIASTORE()
        elif type(in_) is cgen.ArrayPointerType or type(in_) is cgen.ClassType or type(in_) is StringType:
            return self.jvm.emitAASTORE()
        else:
            raise IllegalOperandException(str(in_))

    '''    generate the var directive for a local variable.
    *   @param in the index of the local variable.
    *   @param varName the name of the local variable.
    *   @param inType the type of the local variable.
    *   @param fromLabel the starting label of the scope where the variable is active.
    *   @param toLabel the ending label  of the scope where the variable is active.
    '''
    def emitVAR(self, in_, varName, inType, fromLabel, toLabel, frame):
        #in_: Int
        #varName: String
        #inType: Type
        #fromLabel: Int
        #toLabel: Int
        #frame: Frame
        
        return self.jvm.emitVAR(in_, varName, self.getJVMType(inType), fromLabel, toLabel)

    def emitREADVAR(self, name, inType, index, frame):
        #name: String
        #inType: Type
        #index: Int
        #frame: Frame
        #... -> ..., value
        
        frame.push()
        if type(inType) is IntegerType:
            return self.jvm.emitILOAD(index)
        if type(inType) is FloatType:
            return self.jvm.emitFLOAD(index)
        if type(inType) is BooleanType:
            return self.jvm.emitILOAD(index)
        elif type(inType) is cgen.ArrayPointerType or type(inType) is cgen.ClassType or type(inType) is StringType:
            return self.jvm.emitALOAD(index)
        else:
            raise IllegalOperandException(name)

    ''' generate the second instruction for array cell access
    *
    '''
    def emitREADVAR2(self, name, typ, frame):
        #name: String
        #typ: Type
        #frame: Frame
        #... -> ..., value

        #frame.push()
        raise IllegalOperandException(name)

    '''
    *   generate code to pop a value on top of the operand stack and store it to a block-scoped variable.
    *   @param name the symbol entry of the variable.
    '''
    def emitWRITEVAR(self, name, inType, index, frame):
        #name: String
        #inType: Type
        #index: Int
        #frame: Frame
        #..., value -> ...
        
        frame.pop()

        if type(inType) is IntegerType:
            return self.jvm.emitISTORE(index)
        elif type(inType) is FloatType:
            return self.jvm.emitFSTORE(index)
        if type(inType) is BooleanType:
            return self.jvm.emitISTORE(index)
        elif type(inType) is cgen.ArrayPointerType or type(inType) is cgen.ClassType or type(inType) is StringType:
            return self.jvm.emitASTORE(index)
        else:
            raise IllegalOperandException(name)

    ''' generate the second instruction for array cell access
    *
    '''
    def emitWRITEVAR2(self, name, typ, frame):
        #name: String
        #typ: Type
        #frame: Frame
        #..., value -> ...

        #frame.push()
        raise IllegalOperandException(name)

    ''' generate the field (static) directive for a class mutable or immutable attribute.
    *   @param lexeme the name of the attribute.
    *   @param in the type of the attribute.
    *   @param isFinal true in case of constant; false otherwise
    '''
    def emitATTRIBUTE(self, lexeme, in_, isFinal, value = None):
        #lexeme: String
        #in_: Type
        #isFinal: Boolean
        #value: String

        return self.jvm.emitSTATICFIELD(lexeme, self.getJVMType(in_), False)

    def emitGETSTATIC(self, lexeme, in_, frame):
        #lexeme: String
        #in_: Type
        #frame: Frame

        frame.push()
        return self.jvm.emitGETSTATIC(lexeme, self.getJVMType(in_))

    def emitPUTSTATIC(self, lexeme, in_, frame):
        #lexeme: String
        #in_: Type
        #frame: Frame
        
        frame.pop()
        return self.jvm.emitPUTSTATIC(lexeme, self.getJVMType(in_))

    def emitGETFIELD(self, lexeme, in_, frame):
        #lexeme: String
        #in_: Type
        #frame: Frame

        return self.jvm.emitGETFIELD(lexeme, self.getJVMType(in_))

    def emitPUTFIELD(self, lexeme, in_, frame):
        #lexeme: String
        #in_: Type
        #frame: Frame

        frame.pop()
        frame.pop()
        return self.jvm.emitPUTFIELD(lexeme, self.getJVMType(in_))

    ''' generate code to invoke a static method
    *   @param lexeme the qualified name of the method(i.e., class-name/method-name)
    *   @param in the type descriptor of the method.
    '''
    def emitINVOKESTATIC(self, lexeme, in_, frame):
        #lexeme: String
        #in_: Type
        #frame: Frame

        typ = in_
        list(map(lambda x: frame.pop(), typ.partype))
        if not type(typ.rettype) is VoidType:
            frame.push()
        return self.jvm.emitINVOKESTATIC(lexeme, self.getJVMType(in_))

    ''' generate code to invoke a special method
    *   @param lexeme the qualified name of the method(i.e., class-name/method-name)
    *   @param in the type descriptor of the method.
    '''
    def emitINVOKESPECIAL(self, frame, lexeme=None, in_=None):
        #lexeme: String
        #in_: Type
        #frame: Frame

        if not lexeme is None and not in_ is None:
            typ = in_
            list(map(lambda x: frame.pop(), typ.partype))
            frame.pop()
            if not type(typ.rettype) is VoidType:
                frame.push()
            return self.jvm.emitINVOKESPECIAL(lexeme, self.getJVMType(in_))
        elif lexeme is None and in_ is None:
            frame.pop()
            return self.jvm.emitINVOKESPECIAL()

    ''' generate code to invoke a virtual method
    * @param lexeme the qualified name of the method(i.e., class-name/method-name)
    * @param in the type descriptor of the method.
    '''
    def emitINVOKEVIRTUAL(self, lexeme, in_, frame):
        #lexeme: String
        #in_: Type
        #frame: Frame

        typ = in_
        list(map(lambda x: frame.pop(), typ.partype))
        frame.pop()
        if not type(typ) is VoidType:
            frame.push()
        return self.jvm.emitINVOKEVIRTUAL(lexeme, self.getJVMType(in_))

    '''
    *   generate ineg, fneg.
    *   @param in the type of the operands.
    '''
    def emitNEGOP(self, in_, frame):
        #in_: Type
        #frame: Frame
        #..., value -> ..., result

        if type(in_) is IntegerType:
            return self.jvm.emitINEG()
        else:
            return self.jvm.emitFNEG()

    def emitNOT(self, in_, frame):
        #in_: Type
        #frame: Frame

        label1 = frame.getNewLabel()
        label2 = frame.getNewLabel()
        result = list()
        result.append(emitIFTRUE(label1, frame))
        result.append(emitPUSHCONST("true", in_, frame))
        result.append(emitGOTO(label2, frame))
        result.append(emitLABEL(label1, frame))
        result.append(emitPUSHCONST("false", in_, frame))
        result.append(emitLABEL(label2, frame))
        return ''.join(result)

    '''
    *   generate iadd, isub, fadd or fsub.
    *   @param lexeme the lexeme of the operator.
    *   @param in the type of the operands.
    '''
    def emitADDOP(self, lexeme, in_, frame):
        #lexeme: String
        #in_: Type
        #frame: Frame
        #..., value1, value2 -> ..., result

        frame.pop()
        if lexeme == "+":
            if type(in_) is IntegerType:
                return self.jvm.emitIADD()
            elif type(in_) is FloatType:
                return self.jvm.emitFADD()
        else:
            if type(in_) is IntegerType:
                return self.jvm.emitISUB()
            elif type(in_) is FloatType:
                return self.jvm.emitFSUB()


    '''
    *   generate imul, idiv, fmul or fdiv.
    *   @param lexeme the lexeme of the operator.
    *   @param in the type of the operands.
    '''

    def emitMULOP(self, lexeme, in_, frame):
        #lexeme: String
        #in_: Type
        #frame: Frame
        #..., value1, value2 -> ..., result

        frame.pop()
        if lexeme == "*":
            if type(in_) is IntegerType:
                return self.jvm.emitIMUL()
            else:
                return self.jvm.emitFMUL()
        else:
            if type(in_) is IntegerType:
                return self.jvm.emitIDIV()
            else:
                return self.jvm.emitFDIV()

    def emitDIV(self, frame):
        #frame: Frame

        frame.pop()
        return self.jvm.emitIDIV()

    def emitMOD(self, frame):
        #frame: Frame

        frame.pop()
        return self.jvm.emitIREM()

    '''
    *   generate iand
    '''

    def emitANDOP(self, frame):
        #frame: Frame

        frame.pop()
        return self.jvm.emitIAND()

    '''
    *   generate ior
    '''
    def emitOROP(self, frame):
        #frame: Frame

        frame.pop()
        return self.jvm.emitIOR()

    def emitREOP(self, op, in_, frame):
        #op: String
        #in_: Type
        #frame: Frame
        #..., value1, value2 -> ..., result

        result = list()
        labelF = frame.getNewLabel()
        labelO = frame.getNewLabel()

        frame.pop()
        frame.pop()
        if type(in_) is IntegerType:
            if op == ">":
                result.append(self.jvm.emitIFICMPLE(labelF))
            elif op == ">=":
                result.append(self.jvm.emitIFICMPLT(labelF))
            elif op == "<":
                result.append(self.jvm.emitIFICMPGE(labelF))
            elif op == "<=":
                result.append(self.jvm.emitIFICMPGT(labelF))
            elif op == "!=":
                result.append(self.jvm.emitIFICMPEQ(labelF))
            elif op == "==":
                result.append(self.jvm.emitIFICMPNE(labelF))
        # else:
        #     if op == ">":
        #         result.append(self.jvm.emitIFICMPLE(labelF))
        #     elif op == ">=":
        #         result.append(self.jvm.emitIFICMPLT(labelF))
        #     elif op == "<":
        #         result.append(self.jvm.emitIFICMPGE(labelF))
        #     elif op == "<=":
        #         result.append(self.jvm.emitIFICMPGT(labelF))
        #     elif op == "!=":
        #         result.append(self.jvm.emitIFICMPEQ(labelF))
        #     elif op == "==":
        #         result.append(self.jvm.emitIFICMPNE(labelF))
        result.append(self.emitPUSHCONST("1", IntegerType(), frame))
        frame.pop()
        result.append(self.emitGOTO(labelO, frame))
        result.append(self.emitLABEL(labelF, frame))
        result.append(self.emitPUSHCONST("0", IntegerType(), frame))
        result.append(self.emitLABEL(labelO, frame))
        return ''.join(result)

    def emitRELOP(self, op, in_, trueLabel, falseLabel, frame):
        #op: String
        #in_: Type
        #trueLabel: Int
        #falseLabel: Int
        #frame: Frame
        #..., value1, value2 -> ..., result

        result = list()

        frame.pop()
        frame.pop()
        if op == ">":
            result.append(self.jvm.emitIFICMPLE(falseLabel))
            result.append(self.emitGOTO(trueLabel))
        elif op == ">=":
            result.append(self.jvm.emitIFICMPLT(falseLabel))
        elif op == "<":
            result.append(self.jvm.emitIFICMPGE(falseLabel))
        elif op == "<=":
            result.append(self.jvm.emitIFICMPGT(falseLabel))
        elif op == "!=":
            result.append(self.jvm.emitIFICMPEQ(falseLabel))
        elif op == "==":
            result.append(self.jvm.emitIFICMPNE(falseLabel))
        result.append(self.jvm.emitGOTO(trueLabel))
        return ''.join(result)

    '''   generate the method directive for a function.
    *   @param lexeme the qualified name of the method(i.e., class-name/method-name).
    *   @param in the type descriptor of the method.
    *   @param isStatic <code>true</code> if the method is static; <code>false</code> otherwise.
    '''

    def emitMETHOD(self, lexeme, in_, isStatic, frame):
        #lexeme: String
        #in_: Type
        #isStatic: Boolean
        #frame: Frame

        return self.jvm.emitMETHOD(lexeme, self.getJVMType(in_), isStatic)

    '''   generate the end directive for a function.
    '''
    def emitENDMETHOD(self, frame):
        #frame: Frame

        buffer = list()
        buffer.append(self.jvm.emitLIMITSTACK(frame.getMaxOpStackSize()))
        buffer.append(self.jvm.emitLIMITLOCAL(frame.getMaxIndex()))
        buffer.append(self.jvm.emitENDMETHOD())
        return ''.join(buffer)

    def getConst(self, ast):
        #ast: Literal
        if type(ast) is IntLiteral:
            return (str(ast.value), IntegerType())

    '''   generate code to initialize a local array variable.<p>
    *   @param index the index of the local variable.
    *   @param in the type of the local array variable.
    '''

    '''   generate code to initialize local array variables.
    *   @param in the list of symbol entries corresponding to local array variable.    
    '''

    '''   generate code to jump to label if the value on top of operand stack is true.<p>
    *   ifgt label
    *   @param label the label where the execution continues if the value on top of stack is true.
    '''
    def emitIFTRUE(self, label, frame):
        #label: Int
        #frame: Frame

        frame.pop()
        return self.jvm.emitIFGT(label)

    '''
    *   generate code to jump to label if the value on top of operand stack is false.<p>
    *   ifle label
    *   @param label the label where the execution continues if the value on top of stack is false.
    '''
    def emitIFFALSE(self, label, frame):
        #label: Int
        #frame: Frame

        frame.pop()
        return self.jvm.emitIFLE(label)

    def emitIFICMPGT(self, label, frame):
        #label: Int
        #frame: Frame

        frame.pop()
        return self.jvm.emitIFICMPGT(label)

    def emitIFICMPLT(self, label, frame):
        #label: Int
        #frame: Frame

        frame.pop()
        return self.jvm.emitIFICMPLT(label)    

    '''   generate code to duplicate the value on the top of the operand stack.<p>
    *   Stack:<p>
    *   Before: ...,value1<p>
    *   After:  ...,value1,value1<p>
    '''
    def emitDUP(self, frame):
        #frame: Frame

        frame.push()
        return self.jvm.emitDUP()

    def emitPOP(self, frame):
        #frame: Frame

        frame.pop()
        return self.jvm.emitPOP()

    '''   generate code to exchange an integer on top of stack to a floating-point number.
    '''
    def emitI2F(self, frame):
        #frame: Frame

        return self.jvm.emitI2F()

    ''' generate code to return.
    *   <ul>
    *   <li>ireturn if the type is IntegerType or BooleanType
    *   <li>freturn if the type is RealType
    *   <li>return if the type is null
    *   </ul>
    *   @param in the type of the returned expression.
    '''

    def emitRETURN(self, in_, frame):
        #in_: Type
        #frame: Frame

        if type(in_) is IntegerType:
            frame.pop()
            return self.jvm.emitIRETURN()
        elif type(in_) is FloatType:
            frame.pop()
            return self.jvm.emitFRETURN()
        elif type(in_) is BooleanType:
            frame.pop()
            return self.jvm.emitIRETURN()
        elif type(in_) is VoidType:
            return self.jvm.emitRETURN()


    ''' generate code that represents a label	
    *   @param label the label
    *   @return code Label<label>:
    '''
    def emitLABEL(self, label, frame):
        #label: Int
        #frame: Frame

        return self.jvm.emitLABEL(label)

    ''' generate code to jump to a label	
    *   @param label the label
    *   @return code goto Label<label>
    '''
    def emitGOTO(self, label, frame):
        #label: Int
        #frame: Frame

        return self.jvm.emitGOTO(str(label))

    ''' generate some starting directives for a class.<p>
    *   .source MPC.CLASSNAME.java<p>
    *   .class public MPC.CLASSNAME<p>
    *   .super java/lang/Object<p>
    '''
    def emitPROLOG(self, name, parent):
        #name: String
        #parent: String

        result = list()
        result.append(self.jvm.emitSOURCE(name + ".java"))
        result.append(self.jvm.emitCLASS("public " + name))
        result.append(self.jvm.emitSUPER("java/land/Object" if parent == "" else parent))
        return ''.join(result)

    def emitLIMITSTACK(self, num):
        #num: Int

        return self.jvm.emitLIMITSTACK(num)

    def emitLIMITLOCAL(self, num):
        #num: Int

        return self.jvm.emitLIMITLOCAL(num)

    def emitEPILOG(self):
        file = open(self.filename, "w")
        file.write(''.join(self.buff))
        file.close()

    ''' print out the code to screen
    *   @param in the code to be printed out
    '''
    def printout(self, in_):
        #in_: String

        self.buff.append(in_)

    def clearBuff(self):
        self.buff.clear()
        
from Utils import *

class Frame():
    def __init__(self, name, returnType):
        #name: String
        #returnType: Type

        self.name = name
        self.returnType = returnType
        self.currentLabel = 0
        self.currOpStackSize = 0
        self.maxOpStackSize = 0
        self.currIndex = 0
        self.maxIndex = 0
        self.startLabel = list()
        self.endLabel = list()
        self.indexLocal = list()
        self.conLabel = list()
        self.brkLabel = list()

    def getCurrIndex(self):
        return self.currIndex

    def setCurrIndex(self, index):
        #index: Int
        self.currIndex = index

    '''
    *   return a new label in the method.
    *   @return an integer representing the label.
    '''
    def getNewLabel(self):
        tmp = self.currentLabel
        self.currentLabel = self.currentLabel + 1
        return tmp

    '''
    *   simulate an instruction that pushes a value onto operand stack.
    '''
    def push(self):
        self.currOpStackSize = self.currOpStackSize + 1
        if self.maxOpStackSize < self.currOpStackSize:
            self.maxOpStackSize = self.currOpStackSize

    '''
    *   simulate an instruction that pops a value out of operand stack.
    '''
    def pop(self):
        self.currOpStackSize = self.currOpStackSize - 1
        if self.currOpStackSize < 0:
            raise IllegalRuntimeException("Pop empty stack")

    def getStackSize(self):
        return self.currOpStackSize

    '''
    *   return the maximum size of the operand stack that the method needs to use.
    *   @return an integer that represent the maximum stack size
    '''
    def getMaxOpStackSize(self):
        return self.maxOpStackSize

    '''
    *   check if the operand stack is empty or not.
    *   @throws IllegalRuntimeException if the operand stack is not empty.
    '''
    def checkOpStack(self):
        if self.currOpStackSize != 0:
            raise IllegalRuntimeException("Stack not empty")

    '''
    *   invoked when parsing into a new scope inside a method.<p>
    *   This method will create 2 new labels that represent the starting and ending points of the scope.<p>
    *   Then, these labels are pushed onto corresponding stacks.<p>
    *   These labels can be retrieved by getStartLabel() and getEndLabel().<p>
    *   In addition, this method also saves the current index of local variable.
    '''

    def enterScope(self, isProc):
        #isProc: Boolean
        start = self.getNewLabel()
        end = self.getNewLabel()
        self.startLabel.append(start)
        self.endLabel.append(end)
        self.indexLocal.append(self.currIndex)
        if isProc:
            self.maxOpStackSize = 0
            self.maxIndex = 0

    '''
    *   invoked when parsing out of a scope in a method.<p>
    *   This method will pop the starting and ending labels of this scope
    *   and restore the current index
    '''
    def exitScope(self):
        if not self.startLabel or not self.endLabel or not self.indexLocal:
            raise IllegalRuntimeException("Error when exit scope")
        self.startLabel.pop()
        self.endLabel.pop()
        self.currIndex = self.indexLocal.pop()

    '''
    *   return the starting label of the current scope.
    *   @return an integer representing the starting label
    '''
    def getStartLabel(self):
        if not self.startLabel:
            raise IllegalRuntimeException("None start label")
        return self.startLabel[-1]

    '''
    *   return the ending label of the current scope.
    *   @return an integer representing the ending label
    '''
    def getEndLabel(self):
        if not self.endLabel:
            raise IllegalRuntimeException("None end label")
        return self.endLabel[-1]

    '''
    *   return a new index for a local variable declared in a scope. 
    *   @return an integer that represents the index of the local variable
    '''
    def getNewIndex(self):
        tmp = self.currIndex
        self.currIndex = self.currIndex + 1
        if self.currIndex > self.maxIndex:
            self.maxIndex = self.currIndex
        return tmp

    '''
    *   return the maximum index used in generating code for the current method
    *   @return an integer representing the maximum index
    '''
    def getMaxIndex(self):
        return self.maxIndex

    '''
    *   invoked when parsing into a loop statement.<p>
    *   This method creates 2 new labels that represent the starting and ending label of the loop.<p>
    *   These labels are pushed onto corresponding stacks and are retrieved by getBeginLoopLabel() and getEndLoopLabel().
    '''
    def enterLoop(self):
        con = self.getNewLabel()
        brk = self.getNewLabel()
        self.conLabel.append(con)
        self.brkLabel.append(brk)

    '''
    *   invoked when parsing out of a loop statement.
    *   This method will take 2 labels representing the starting and ending labels of the current loop out of its stacks.
    '''
    def exitLoop(self):
        if not self.conLabel or not self.brkLabel:
            raise IllegalRuntimeException("Error when exit loop")
        self.conLabel.pop()
        self.brkLabel.pop()

    '''
    *   return the label of the innest enclosing loop to which continue statement would jump
    *   @return an integer representing the continue label
    '''
    def getContinueLabel(self):
        if not self.conLabel:
            raise IllegalRuntimeException("None continue label")
        return self.conLabel[-1]

    '''
    *   return the label of the innest enclosing loop to which break statement would jump
    *   @return an integer representing the break label
    '''
    def getBreakLabel(self):
        if not self.brkLabel:
            raise IllegalRuntimeException("None break label")
        return self.brkLabel[-1]






        
