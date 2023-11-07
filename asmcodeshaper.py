'''
-@author: Tyler Ray
-@date: 11/6/2023

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
        for scope in self.code:
            indent = 5
            output += ' ' * indent + scope + ':' + '\n'
            for block in self.code[scope]:
                indent = 8
                output += ' ' * indent + block + ':' + '\n'
                for line in self.code[scope][block]:
                    indent = 11
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

global jumpTable

jumpTable = {
    '==': 'jne',
    '!=': 'je',
    '>': 'jle',
    '<': 'jge',
    '>=': 'jl',
    '<=': 'jg',
    '&&': 'and',
    '||': 'or',
}

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
    stackSpaceNeeded = _figureOutHowMuchStackSpaceWeNeed(symbolTable)
    asmCode.addLine(currentScope, currentBlock, "sub rsp, " + str(stackSpaceNeeded))#Eventually we will need to change this to be the size of the local variables

def _figureOutHowMuchStackSpaceWeNeed(symbolTable):
    global currentScope

    spaceNeeded = 0

    arguments = symbolTable.get_args(currentScope)
    variables = symbolTable.get_vars(currentScope)

    for argument in arguments:
        if arguments[argument] == 'int' or arguments[argument] == 'char':
            spaceNeeded += 4

        elif arguments[argument] == 'float':
            spaceNeeded += 8

        elif arguments[argument] == 'double':
            spaceNeeded += 16
    
    for variable in variables:
        if variables[variable][0] == 'int' or variables[variable][0] == 'char': #I used to put what number something was in the symbol Table, the type was at [0] and the number was at [1].
            spaceNeeded += 4
        
        elif variables[variable][0] == 'float':
            spaceNeeded += 8
        
        elif variables[variable][0] == 'double':
            spaceNeeded += 16
    

    return spaceNeeded



#Creates our epilogue for when we close out a function
def _createEpilogue():
    global currentScope
    global currentBlock
    global asmCode

    asmCode.addLine(currentScope, currentBlock, "leave")
    asmCode.addLine(currentScope, currentBlock, "ret")
    
#Shapes each functions code into assembly
def _codeShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister


    statementIndicator = codeLine[-1]
    statementIndicatorForIfs = codeLine[0] #I don't know why I did this, but for some reason I left its at the front. It makes it look nice while debugging but not for consistency.
    
    hasReturn = False
    if statementIndicator == 'return':
        _returnShaper(codeLine)
    elif statementIndicator == 'assign':
        _assignShaper(codeLine)
    elif statementIndicator == 'decl':
        print(codeLine)
        _assignShaper(codeLine) #These are the same thing
    elif statementIndicatorForIfs == 'if':
        _ifShaper(codeLine)
    elif statementIndicator == 'goto':
        _gotoShaper(codeLine)

    if hasReturn == False:#Set Eax to 0 if there is no return statement
        pass

#Shapes a return statement into assembly
def _returnShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    if re.match(cc.numbers, codeLine[0]):#Checking to see if we need to refrence memory or just a number
        returnCode = "mov " + str(currentRegister.getRegister()) + ', ' + codeLine[0]
    else:
        returnCode = "mov " + str(currentRegister.getRegister()) + ', ' '[' + codeLine[0] + "]"

    asmCode.addLine(currentScope, currentBlock, returnCode)

#Shapes an assignment statement into assembly
def _assignShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode
    global jumpTable

    if re.match(cc.exprOps, codeLine[2]): #Meaning we have an expression
        _exprShaper(codeLine)
    elif codeLine[2] in jumpTable: #Meaning we have an if statement
        _multipleIfShaper(codeLine)
    else:
        register = currentRegister.getRegister()
        if not re.match(cc.numbers, codeLine[1]):#is it just a number or a variable
            assignCode = "mov " + register + ', ' '[' + codeLine[1] + "]"
            asmCode.addLine(currentScope, currentBlock, assignCode)
            assignCode = "mov " + '[' + codeLine[0] + '], ' + register
            asmCode.addLine(currentScope, currentBlock, assignCode)
        else:
            asmCode.addLine(currentScope, currentBlock, "mov " + '[' + codeLine[0] + '], ' + codeLine[1])

#Figures out what instruction we need to use for an expression
def _exprShaper(codeLine):
    operator = codeLine[2]

    if operator == '+':
        _operatorShaper(codeLine, 'add')
    elif operator == '-':
        _operatorShaper(codeLine, 'sub')
    elif operator == '*':
        _operatorShaper(codeLine, 'mul')
    elif operator == '/':
        _operatorShaper(codeLine, 'div')

#Shapes an expression into assembly
def _operatorShaper(codeLine, instruction):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    register = currentRegister.getRegister()

    if re.match(cc.numbers, codeLine[1]):
        asmCode.addLine(currentScope, currentBlock, "mov " + register + ', ' + codeLine[1])
    else:
        asmCode.addLine(currentScope, currentBlock, "mov " + register + ', ' + '[' + codeLine[1] + "]")
    
    if re.match(cc.numbers, codeLine[3]):
        asmCode.addLine(currentScope, currentBlock, instruction + ' ' + register + ', ' + codeLine[3])
    else:
        secondRegister = currentRegister.getRegister()
        asmCode.addLine(currentScope, currentBlock, "mov " + secondRegister + ', ' + '[' + codeLine[3] + "]")
        asmCode.addLine(currentScope, currentBlock, instruction + ' ' + register + ', ' + secondRegister)

    asmCode.addLine(currentScope, currentBlock, "mov " + '[' + codeLine[0] + '], ' + register)


def _ifShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode
    global jumpTable
    jumpExpression = jumpTable[codeLine[2]]

    if not (jumpExpression == 'and' or jumpExpression == 'or'):
        register = currentRegister.getRegister()

        if re.match(cc.numbers, codeLine[1]):
            asmCode.addLine(currentScope, currentBlock, "mov " + register + ', ' + codeLine[1])
        else:
            asmCode.addLine(currentScope, currentBlock, "mov " + register + ', ' + '[' + codeLine[1] + "]")
        

        

        if re.match(cc.numbers, codeLine[3]):
            asmCode.addLine(currentScope, currentBlock, "cmp " + register + ', ' + codeLine[3])
        else:
            secondRegister = currentRegister.getRegister()
            asmCode.addLine(currentScope, currentBlock, "mov " + secondRegister + ', ' + '[' + codeLine[3] + "]")
            asmCode.addLine(currentScope, currentBlock, "cmp " + register + ', ' + secondRegister)
        
        asmCode.addLine(currentScope, currentBlock, jumpExpression + ' L' + codeLine[7])
    else:
        _multipleIfConditional(codeLine)

def _gotoShaper(codeLine):
    global currentScope
    global currentBlock
    global asmCode

    asmCode.addLine(currentScope, currentBlock, 'jmp ' + codeLine[0])

def _multipleIfShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    register = currentRegister.getRegister()

    if re.match(cc.numbers, codeLine[1]):
        asmCode.addLine(currentScope, currentBlock, "mov " + register + ', ' + codeLine[1])
    else:
        asmCode.addLine(currentScope, currentBlock, "mov " + register + ', ' + '[' + codeLine[1] + "]")
    
    jumpExpression = jumpTable[codeLine[2]]

    if jumpExpression == 'and' or jumpExpression == 'or':
        _multipleIfConditional(codeLine, register)

    elif re.match(cc.numbers, codeLine[3]):
        asmCode.addLine(currentScope, currentBlock, "cmp " + register + ', ' + codeLine[3])
    else:
        secondRegister = currentRegister.getRegister()
        asmCode.addLine(currentScope, currentBlock, "mov " + secondRegister + ', ' + '[' + codeLine[3] + "]")
        asmCode.addLine(currentScope, currentBlock, "cmp " + register + ', ' + secondRegister)
    
    asmCode.addLine(currentScope, currentBlock, jumpExpression + ' REPLACE')
    
def _multipleIfConditional(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode
    global jumpTable

    jumpEnd = 'L' + codeLine[7]

    asmBlock = asmCode.code[currentScope][currentBlock]

    newAsmBlock = []

    for line in asmBlock:
        if line[-7:] == 'REPLACE':
            tempLine = line[:-7] + jumpEnd
            newAsmBlock.append(tempLine)
        else:
            newAsmBlock.append(line)

    asmCode.code[currentScope][currentBlock] = newAsmBlock
