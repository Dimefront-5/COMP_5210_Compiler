'''
-@author: Tyler Ray
-@date: 11/2/2023

- This file will convert our optimized 3 address code into assembly code
- ***Work in progress***
'''

import re
import compilerconstants as cc

supportedInstructions = [
    "add",
    "sub",
    "mul",
    "div",
    "push",
    "pop",
    "call",
    "ret",
    "cmp",
    "jmp",
    "Call",
    "Ret",
    "Leave",
]


codeShapes = {
    "return":"mov r1, x.....\
              ret",

    "assign": "mov [x], r1",

    "add": "mov r1, [x]\
            add r1, y\
            assign",

    "sub": "mov r1, [x]\
            sub r1, y\
            assign",

    "mul": "mov r1, [x]\
            mul r1, y\
            assign",

    "div": "mov r1, [x]\
            div r1, y\
            assign",

    "if": "mov r1, [x]\
           cmp r1, y\
           jmp... label",


}

class assemblyCode:
    def __init__(self):
        self.code = {}
    
    def addScope(self, scope):
        self.code[scope] = {}

    def addBlock(self, scope, block):
        self.code[scope][block] = []

    def addLine(self, scope, block, line):
        self.code[scope][block].append(line)

    def __str__(self):
        output = ''
        indent = 5
        for scope in self.code:
            output += ' ' * indent + scope + ':' + '\n'
            indent = 8
            for block in self.code[scope]:
                output += ' ' * indent + block + ':' + '\n'
                indent = 11
                for line in self.code[scope][block]:
                    output += ' ' * indent + line + '\n'
        return output

class register:
    def __init__(self):
        self.registerNumber = 0

    def getRegister(self):
        register = "r" + str(self.registerNumber)
        self.registerNumber += 1
        return register
    

global currentRegister

currentRegister = register()

global asmCode

asmCode = assemblyCode()

global currentScope

currentScope = 'global'

global currentBlock
    
def codeShaper(threeAddrCode, symbolTable):
    global asmCode
    _generateAssemblyCode(threeAddrCode, symbolTable)

    return asmCode

#------ Inward Facing modules

def _generateAssemblyCode(threeAddrCode, symbolTable):
    global currentScope
    global currentBlock
    global asmCode

    for scope in threeAddrCode:
        if isinstance(threeAddrCode[scope], dict):#Ignoring global variables for now
            asmCode.addScope(scope)
            currentScope = scope
            currentBlock = list(threeAddrCode[scope].keys())[0]
            asmCode.addBlock(scope, currentBlock)
            _createPrelude(symbolTable)
            for block in threeAddrCode[scope]:
                if block != currentBlock: #Want to skip first block since we already made it
                    asmCode.addBlock(scope, block)

                currentBlock = block
                for key, line in threeAddrCode[scope][block].items():
                    _codeShaper(line)
            
            _createEpilogue()
    
def _createPrelude(symbolTable):
    global currentScope
    global currentBlock
    global asmCode

    asmCode.addLine(currentScope, currentBlock, "push rbp")
    asmCode.addLine(currentScope, currentBlock, "mov rbp, rsp")
    asmCode.addLine(currentScope, currentBlock, "sub rsp, 16")#Eventually we will need to change this to be the size of the local variables

def _createEpilogue():
    global currentScope
    global currentBlock
    global asmCode

    asmCode.addLine(currentScope, currentBlock, "leave")
    asmCode.addLine(currentScope, currentBlock, "ret")
    

def _codeShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister


    statementIndicator = codeLine[-1]
    statementIndicatorForIfs = codeLine[0] #I don't know why I did this, but for some reason I left its at the front. It makes it look nice while debugging but not for consistency.
    
    hasReturn = False
    if statementIndicator == 'return':
        _returnShaper(codeLine)


    if hasReturn == False:#Set Eax to 0 if there is no return statement
        pass


def _returnShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    if re.match(cc.numbers, codeLine[0]):
        returnCode = "mov r1, " + codeLine[0]
    else:
        returnCode = "mov r1, [" + codeLine[0] + "]"
        
    asmCode.addLine(currentScope, currentBlock, returnCode)
