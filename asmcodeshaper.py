'''
-@author: Tyler Ray
-@date: 11/7/2023

- This file will convert our optimized 3 address code into assembly code
- ***Work in progress***
'''

import re
import compilerconstants as cc
import networkx as nx

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
    "xor",
    "shl",
    "shr"
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

    _registrySetter()

# Walks through our code and finds every register that is used and when it is used
def _registrySetter():
    global asmCode

    code = asmCode.code

    registersInBlock = {}
    lineNumber = 0
    for scope in code:
        for block in code[scope]:
            registersInBlock[block] = []
            lineNumber = 0
            for line in code[scope][block]:
                lineNumber += 1
                splitLine = line.split(' ')
                if len(splitLine) > 1:
                    afterInstruction = splitLine[1][:-1]
                    if afterInstruction[0:1] == 'r' and afterInstruction[1:].isnumeric():
                        registersInBlock[block].append([afterInstruction, lineNumber])

                    if len(splitLine) > 2:
                        secondAfterInstruction = splitLine[2]
                        if secondAfterInstruction[0:1] == 'r' and secondAfterInstruction[1:].isnumeric():
                            registersInBlock[block].append([secondAfterInstruction, lineNumber])

    _registerAllocator(registersInBlock) 

#Checks to see if we need to do live analysis or not
def _registerAllocator(registersInBlock):
    livenessAnalysisPerBlock = {}
    for block in registersInBlock:
        livenessAnalysisPerBlock[block] = {}
        for register in registersInBlock[block]:
            if register[0] not in livenessAnalysisPerBlock[block]:
                livenessAnalysisPerBlock[block][register[0]] = [register[1], register[1]]
            else:
                livenessAnalysisPerBlock[block][register[0]][1] = register[1]
    
    newMapping = {}
    for block in livenessAnalysisPerBlock:
        newMapping[block] = {}
        registerCount = 0
        for register in livenessAnalysisPerBlock[block]:
            registerCount += 1

        if registerCount > 15:
            _liveAnalysis(livenessAnalysisPerBlock[block], block)

        else:#Will assign each register to a numbered register
            registerList = ['eax', 'ebx', 'ecx', 'edx', 'esi', 'edi', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
            for register in livenessAnalysisPerBlock[block]:
                newMapping[block][register] = registerList[0]
                registerList.pop(0)
    
    _registerReplacer(newMapping)

#Replaces our registers with the ones we have assigned
def _registerReplacer(newMapping):
    global asmCode

    newBlock = {}
    for scope in asmCode.code:
        for block in asmCode.code[scope]:
            newBlock[block] = []
            for line in asmCode.code[scope][block]:
                splitLine = line.split(' ')
                if len(splitLine) > 1:
                    afterInstruction = splitLine[1][:-1]
                    if afterInstruction[0:1] == 'r' and afterInstruction[1:].isnumeric():
                        splitLine[1] = newMapping[block][afterInstruction] + ','

                        if len(splitLine) > 2: #is the second after instruction a register?
                            secondAfterInstruction = splitLine[2]
                            if secondAfterInstruction[0:1] == 'r' and secondAfterInstruction[1:].isnumeric():
                                splitLine[2] = newMapping[block][secondAfterInstruction]
                                newBlock[block].append(' '.join(splitLine))
                            else:
                                newBlock[block].append(' '.join(splitLine))
                        else:
                            newBlock[block].append(' '.join(splitLine))

                    elif len(splitLine) > 2:
                        secondAfterInstruction = splitLine[2]
                        if secondAfterInstruction[0:1] == 'r' and secondAfterInstruction[1:].isnumeric():
                            splitLine[2] = newMapping[block][secondAfterInstruction]
                            newBlock[block].append(' '.join(splitLine))
                        else:
                            newBlock[block].append(line)
                    else:
                        newBlock[block].append(line)
                else:
                    newBlock[block].append(line)
    
            asmCode.code[scope][block] = newBlock[block]
        

def _liveAnalysis(livenessAnalysis, block):
    pass


#Creates our prelude for when we start a function
def _createPrelude(symbolTable):
    global currentScope
    global currentBlock
    global asmCode

    asmCode.addLine(currentScope, currentBlock, "push ebp")
    asmCode.addLine(currentScope, currentBlock, "mov ebp, esp")
    stackSpaceNeeded = _figureOutHowMuchStackSpaceWeNeed(symbolTable)
    asmCode.addLine(currentScope, currentBlock, "sub esp, " + str(stackSpaceNeeded))#Eventually we will need to change this to be the size of the local variables

#Figures out how much stack space we need for a function
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

    returnBlock = currentScope + 'Return'

    asmCode.addBlock(currentScope, returnBlock)#We add a block for our return statement so if there are any other returns in the code they can jump straight to it
    asmCode.addLine(currentScope, returnBlock, "leave")
    asmCode.addLine(currentScope, returnBlock, "ret")
    

            
    
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
        _assignShaper(codeLine) #These are the same thing
    elif statementIndicator == 'functionCall':
        _callShaper(codeLine)
    elif statementIndicatorForIfs == 'if':
        _ifShaper(codeLine)
    elif statementIndicator == 'goto':
        _gotoShaper(codeLine)

#Shapes a return statement into assembly
def _returnShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    if re.match(cc.numbers, codeLine[0]):#Checking to see if we need to refrence memory or just a number
        returnCode = "mov eax" + ', ' + codeLine[0]
    else:
        returnCode = "mov eax" + ', ' '[' + codeLine[0] + "]"

    asmCode.addLine(currentScope, currentBlock, returnCode)
    asmCode.addLine(currentScope, currentBlock, 'jmp ' + currentScope + 'Return')

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
        _shiftChecking(codeLine, 'mul')
    elif operator == '/':
        _shiftChecking(codeLine, 'div')

#Will check for some basic optimizations for multiplication and division
#Then will see if we can shift it instead of using the actual operation
def _shiftChecking(codeLine, operation):
    if codeLine[1] == '1':#If we are multiplying by 1, we can just move the number into the variable
        asmCode.addLine(currentScope, currentBlock, "mov " + '[' + codeLine[0] + '], ' + codeLine[3])

    elif codeLine[3] == '1':
        asmCode.addLine(currentScope, currentBlock, "mov " + '[' + codeLine[0] + '], ' + codeLine[1])

    elif codeLine[1] == '0' or codeLine[3] == '0':#If either is 0, we can just move 0 into the variable
        asmCode.addLine(currentScope, currentBlock, "mov " + '[' + codeLine[0] + '], ' + codeLine[1])

    elif codeLine[1].isnumeric() and is_power_of_2(int(codeLine[1])):
        if operation == 'div':
            _shiftFinder(codeLine, 1, 3, 'right')
        else:
            _shiftFinder(codeLine, 1, 3, 'left')
    elif codeLine[3].isnumeric() and is_power_of_2(int(codeLine[3])):#If we are dividing by an even number, we can just shift the number to the left
        if operation == 'div':
            _shiftFinder(codeLine, 3, 1, 'right')
        else:
            _shiftFinder(codeLine, 3, 1, 'left')
    else:
        _operatorShaper(codeLine, operation)

#I had ChatGPT generate this function for me
def is_power_of_2(num):
    # Check if the number is greater than 0 and has only one bit set to 1.
    # A power of 2 in binary has only one bit set.
    return num > 0 and (num & (num - 1)) == 0

def _shiftFinder(codeLine, codeLineIndex, oppositeIndex, direction):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    shiftNumber = get_shift_count(int(codeLine[codeLineIndex]))
    register = currentRegister.getRegister()

    if re.match(cc.numbers, codeLine[codeLineIndex]):
        asmCode.addLine(currentScope, currentBlock, "mov " + register + ', ' + codeLine[oppositeIndex])
    else:
        asmCode.addLine(currentScope, currentBlock, "mov " + register + ', ' + '[' + codeLine[oppositeIndex] + "]")

    if direction == 'left':
        asmCode.addLine(currentScope, currentBlock, "shl " + register + ', ' + str(shiftNumber))
    else:
        asmCode.addLine(currentScope, currentBlock, "shr " + register + ', ' + str(shiftNumber))

    asmCode.addLine(currentScope, currentBlock, "mov " + '[' + codeLine[0] + '], ' + register)

#I had ChatGPT generate this function for me
def get_shift_count(num):
    if num <= 0:
        return 0  # Handling the case when num is not a power of 2.
    
    shift_count = 0
    while (num & 1) == 0:
        num >>= 1
        shift_count += 1

    return shift_count

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

#shapes our call statements
def _callShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    for argument in codeLine[1]:
        if re.match(cc.numbers, argument):
            asmCode.addLine(currentScope, currentBlock, "push " + argument)
        elif argument[0] == '\'' or argument[0] == '\"':
            asmCode.addLine(currentScope, currentBlock, "push " + argument)
        else:
            asmCode.addLine(currentScope, currentBlock, "push [" + argument + "]")

    asmCode.addLine(currentScope, currentBlock, "call " + codeLine[0])
    asmCode.addLine(currentScope, currentBlock, 'xor rax, rax')

#Shapes our if statements   
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
        _multipleIfConditional(codeLine, jumpExpression)

#Shapes our gotos
def _gotoShaper(codeLine):
    global currentScope
    global currentBlock
    global asmCode

    if len(asmCode.code[currentScope][currentBlock]) == 0 or not asmCode.code[currentScope][currentBlock][-1][0:3] == 'jmp':#If there is a jump at the end of the block, we don't need to add another one This is for return statements in loops
        asmCode.addLine(currentScope, currentBlock, 'jmp ' + codeLine[0])

#Sets up for multiple if statement conditionals
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

    if re.match(cc.numbers, codeLine[3]):
        asmCode.addLine(currentScope, currentBlock, "cmp " + register + ', ' + codeLine[3])
    else:
        secondRegister = currentRegister.getRegister()
        asmCode.addLine(currentScope, currentBlock, "mov " + secondRegister + ', ' + '[' + codeLine[3] + "]")
        asmCode.addLine(currentScope, currentBlock, "cmp " + register + ', ' + secondRegister)
    
    asmCode.addLine(currentScope, currentBlock, jumpExpression + ' REPLACE')#We leave this like this so we can change it later


#Fixes our multiple conditional statements so it turns into assembyl correctly
def _multipleIfConditional(codeLine, operator):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode
    global jumpTable

    #    if operator == 'or', We will need to swap the first operator around so it acts as an if statement
    oppositeJumps = {
        'jne': 'je',
        'je': 'jne',
        'jle': 'jg',
        'jge': 'jl',
        'jl': 'jge',
        'jg': 'jle',
    }
    
    jumpEnd = 'L' + codeLine[7]

    asmBlock = asmCode.code[currentScope][currentBlock]

    newAsmBlock = []

    firstConditional = False
    for line in asmBlock:
        if line[-7:] == 'REPLACE':
            if operator == 'or' and firstConditional == False:#We only change the first conditional of an or statement
                oppositeJump = oppositeJumps[line[0:3]]
                newFinalJump = currentBlock[:1] + str(int(currentBlock[1:]) + 1) 
                tempLine = oppositeJump + ' ' + newFinalJump
            else:
                tempLine = line[:-7] + jumpEnd

            if firstConditional == False:
                firstConditional = True

            newAsmBlock.append(tempLine)
        else:
            newAsmBlock.append(line)

    asmCode.code[currentScope][currentBlock] = newAsmBlock
