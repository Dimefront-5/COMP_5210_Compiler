'''
-@author: Tyler Ray
-@date: 11/16/2023

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
    "xor",
    "shl",
    "shr"
]



class assemblyCode:
    def __init__(self):
        self.code = {}
    
    def addScope(self, scope):
        self.code[scope] = {}

    def addBlock(self, scope, block):
        self.code[scope][block] = []

    def addLine(self, scope, block, line):#Line will be a list of the instruction and the two values
        self.code[scope][block].append(line)

    def __str__(self):
        output = ''
        for scope in self.code:
            if scope != 'global':
                indent = 0
                output += ' ' * indent + scope + ':' + '\n'
                for block in self.code[scope]:
                    indent = 0
                    output += ' ' * indent + block + ':' + '\n'

                    for line in self.code[scope][block]:
                        indent = 3
                        for index, word in enumerate(line):
                            if index == 0:
                                output += ' ' * indent + word + ' '
                            elif index == 1:
                                output += word
                            elif index == 2:
                                output += ', ' + word

                        output += '\n'
            else:
                globalVars = self.code[scope]
                temp = ''
                for variableName in globalVars:
                    temp += variableName + ':\n'
                    for line in globalVars[variableName]:
                        temp += ' ' * 3 + line[0] + ' ' + line[1] +  '\n'
                output = temp + output
                
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

    returnedASMCode = _generateAssemblyCode(threeAddrCode, symbolTable)

    return returnedASMCode


#------ Inward Facing modules

def _generateAssemblyCode(threeAddrCode, symbolTable):
    global currentScope
    global currentBlock
    global asmCode

    for scope in threeAddrCode:
        if isinstance(threeAddrCode[scope], dict):
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
        else:
            asmCode.addScope('global')
            _addingGlobalVars(symbolTable)


    newMappings = _registrySetter()

    variableMapping = _changingMemoryReferences(symbolTable)

    recreatedASMCode = _recreatingCode(newMappings, variableMapping)
    
    return recreatedASMCode



#Creates our prelude for when we start a function
def _createPrelude(symbolTable):
    global currentScope
    global currentBlock
    global asmCode

    asmCode.addLine(currentScope, currentBlock, ["push", "rbp"])
    asmCode.addLine(currentScope, currentBlock, ["mov", "rbp", "rsp"])
    stackSpaceNeeded = _figureOutHowMuchStackSpaceWeNeed(symbolTable)
    asmCode.addLine(currentScope, currentBlock, ["sub", "rsp", str(stackSpaceNeeded)])

#Figures out how much stack space we need for a function
def _figureOutHowMuchStackSpaceWeNeed(symbolTable):
    global currentScope

    spaceNeeded = 0

    arguments = symbolTable.get_args(currentScope)
    variables = symbolTable.get_vars(currentScope)

    for argument in arguments: #The ifs aren't needed sionce we don't care about floats and doubles anymore. I left them in for now just in case
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
    
    spaceNeeded += 4
    return spaceNeeded

#Creates our epilogue for when we close out a function
def _createEpilogue():
    global currentScope
    global currentBlock
    global asmCode

    returnBlock = currentScope + 'Return'

    asmCode.addBlock(currentScope, returnBlock)#We add a block for our return statement so if there are any other returns in the code they can jump straight to it
    asmCode.addLine(currentScope, returnBlock, ["leave"])
    asmCode.addLine(currentScope, returnBlock, ["ret"])


#Adds our global variables to the assembly code
def _addingGlobalVars(symbolTable):
    global_vars = symbolTable.get_vars('global')

    for var in global_vars:
        asmCode.addBlock('global', var)
        if global_vars[var][0] == 'int' or global_vars[var][0] == 'float':
            if len(global_vars[var]) > 1:
                asmCode.addLine('global', var, [f'.long',f'{global_vars[var][1]}'])
            else:
                asmCode.addLine('global', var, ['.long', 0])

        elif global_vars[var][0] == 'char':
            if len(global_vars[var]) > 1:
                asmCode.addLine('global', var, [f'.byte', f'{global_vars[var][1]}'])
            else:
                asmCode.addLine('global', var, ['.byte', '0'])


def _recreatingCode(newMappings, variableMapping):
    global asmCode

    newAsmCode = assemblyCode()

    currentCode = asmCode.code

    for scope in currentCode:
        newAsmCode.addScope(scope)
        for block in currentCode[scope]:
            newAsmCode.addBlock(scope, block)
            for line in currentCode[scope][block]:
                if len(line) > 1:
                    if _isItARegister(line[1], newMappings, block) is True:
                        line[1] = newMappings[block][line[1]]

                    if line[1][:1] == '[' and line[1][-1:] == ']':
                        if line[1][1:-1] in variableMapping:
                            line[1] = variableMapping[line[1][1:-1]]

                        elif 'global' in currentCode and line[1][1:-1] in currentCode['global']:
                            line[1] = line[1][1:-1] + '[' + 'rip' + ']'
                        
                    if len(line) > 2:
                        if _isItARegister(line[2], newMappings, block) is True:
                            line[2] = newMappings[block][line[2]]

                        if line[2][:1] == '[' and line[2][-1:] == ']':
                            if line[2][1:-1] in variableMapping:
                                line[2] = variableMapping[line[2][1:-1]]

                            elif 'global' in currentCode and line[2][1:-1] in currentCode['global']:
                                line[2] = line[2][1:-1] + '[' + 'rip' + ']'
                        
                    newAsmCode.addLine(scope, block, line)

                else:
                    newAsmCode.addLine(scope, block, line)
    return newAsmCode

def _isItARegister(line, newMappings, block):
    if line[:1] == 'r' and line[1:].isnumeric():
        if line in newMappings[block]:
            return True
    return False


def _registrySetter():
    global asmCode

    code = asmCode.code

    registersInBlock = {}
    for scope in code:
        for block in code[scope]:
            registersInBlock[block] = {}
            for index, line in enumerate(code[scope][block]):
                if len(line) > 1:
                    if line[1][:1] == 'r' and line[1][1:].isnumeric():
                        if line[1] not in registersInBlock[block]:
                            registersInBlock[block][line[1]] = [index, index]
                        else:
                            registersInBlock[block][line[1]][1] = index

                    if len(line) > 2:
                        if line[2][:1] == 'r' and line[2][1:].isnumeric():
                            if line[2] not in registersInBlock[block]:
                                registersInBlock[block][line[1]] = [index, index]
                            else:
                                registersInBlock[block][line[2]][1] = index

    return _registerAllocator(registersInBlock)


def _registerAllocator(registersInBlock):
    newMappings = {}

    for block in registersInBlock:
        newMappings[block] = {}

        numberOfRegisters = len(registersInBlock[block])

        if numberOfRegisters > 14:
            _liveAnalysis(registersInBlock[block], block)
        else:
            registerList = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
            for register in registersInBlock[block]:
                newMappings[block][register] = registerList[0]
                registerList.pop(0)

    return newMappings


def _liveAnalysis(registersInBlock, block):
    pass


def _changingMemoryReferences(symbolTable):
    stackAddress = 4
    variableMapping = {}
    for scope in symbolTable.symbolTable:
        if scope != 'global':
            variables = symbolTable.get_vars(scope)
            arguments = symbolTable.get_args(scope)

            for variable in variables:
                if variables[variable][0] == 'int' or variables[variable][0] == 'char':#We used to put the value in the symbol table so thats why there is a 0 here
                    variableMapping[variable] = f'[rbp-{stackAddress}]'
                    stackAddress += 4
                elif variables[variable][0] == 'float':
                    variableMapping[variable] = f'[rbp - {stackAddress}]'
                    stackAddress += 8
                elif variables[variable][0] == 'double':
                    variableMapping[variable] = f'[rbp - {stackAddress}]'
                    stackAddress += 16

            for argument in arguments:
                if arguments[argument] == 'int' or arguments[argument] == 'char':#We don't put the number the argument is at in the symbol table anymore, so we don't need to check for it
                    if arguments[argument] == 'char':
                        variableMapping[f'\'{argument}\''] = f'[rbp-{stackAddress}]'

                    else:
                        variableMapping[argument] = f'[rbp-{stackAddress}]'
                    stackAddress += 4
                elif arguments[argument] == 'float':
                    variableMapping[argument] = f'[rbp - {stackAddress}]'
                    stackAddress += 8
                elif arguments[argument] == 'double':
                    variableMapping[argument] = f'[rbp - {stackAddress}]'
                    stackAddress += 16
            
    return variableMapping
                

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
        returnCode = ["mov", "rax", codeLine[0]]
    else:
        returnCode = ["mov", "rax", "[" + codeLine[0] + "]"]

    asmCode.addLine(currentScope, currentBlock, returnCode)
    asmCode.addLine(currentScope, currentBlock, ["jmp", currentScope + 'Return'])#We jump to the return block we make in the epilogue

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
            assignCode = ["mov", register, "[" + codeLine[1] + "]"]
            asmCode.addLine(currentScope, currentBlock, assignCode)
            assignCode = ["mov", "[" + codeLine[0] + "]", register]
            asmCode.addLine(currentScope, currentBlock, assignCode)
        else:
            asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", codeLine[1]])



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
        asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", codeLine[3]])

    elif codeLine[3] == '1':
        asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", codeLine[1]])

    elif codeLine[1] == '0' or codeLine[3] == '0':#If either is 0, we can just move 0 into the variable
        asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", '0'])

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


#Looks to see if we can use shifts instead of the actual operation
def _shiftFinder(codeLine, codeLineIndex, oppositeIndex, direction):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    shiftNumber = get_shift_count(int(codeLine[codeLineIndex]))
    register = currentRegister.getRegister()

    if re.match(cc.numbers, codeLine[codeLineIndex]):
        asmCode.addLine(currentScope, currentBlock, ["mov", register, codeLine[codeLineIndex]])
    else:
        asmCode.addLine(currentScope, currentBlock, ["mov", register , '[' + codeLine[oppositeIndex] + "]"])

    if direction == 'left':
        asmCode.addLine(currentScope, currentBlock, ["shl", register , str(shiftNumber)])
    else:
        asmCode.addLine(currentScope, currentBlock, ["shr" ,register, str(shiftNumber)])

    asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", register])


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
        asmCode.addLine(currentScope, currentBlock, ["mov", register, codeLine[1]])
    else:
        asmCode.addLine(currentScope, currentBlock, ["mov", register, '[' + codeLine[1] + "]"])
    
    if re.match(cc.numbers, codeLine[3]):
        asmCode.addLine(currentScope, currentBlock, [instruction, register, codeLine[3]])
    else:
        secondRegister = currentRegister.getRegister()
        asmCode.addLine(currentScope, currentBlock, ["mov", secondRegister, '[' + codeLine[3] + "]"])
        asmCode.addLine(currentScope, currentBlock, [instruction, register, secondRegister])

    asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", register])



#shapes our call statements
def _callShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    for argument in codeLine[1]:
        if re.match(cc.numbers, argument):
            asmCode.addLine(currentScope, currentBlock, ["push", argument])
        elif argument[0] == '\'' or argument[0] == '\"':
            asmCode.addLine(currentScope, currentBlock, ["push", argument])
        else:
            asmCode.addLine(currentScope, currentBlock, ["push", "[" + argument + "]"])

    asmCode.addLine(currentScope, currentBlock, ["call", codeLine[0]])
    asmCode.addLine(currentScope, currentBlock, ["xor", "rax", "rax"])


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
            asmCode.addLine(currentScope, currentBlock, ["mov", register, codeLine[1]])
        else:
            asmCode.addLine(currentScope, currentBlock, ["mov", register, '[' + codeLine[1] + "]"])
        
        if re.match(cc.numbers, codeLine[3]):
            asmCode.addLine(currentScope, currentBlock, ["cmp", register, codeLine[3]])
        else:
            secondRegister = currentRegister.getRegister()
            asmCode.addLine(currentScope, currentBlock, ["mov", secondRegister, '[' + codeLine[3] + "]"])
            asmCode.addLine(currentScope, currentBlock, ["cmp", register, secondRegister])
        
        asmCode.addLine(currentScope, currentBlock, [jumpExpression, 'L' + codeLine[7]])
    else:
        _multipleIfConditional(codeLine, jumpExpression)


#Shapes our gotos
def _gotoShaper(codeLine):
    global currentScope
    global currentBlock
    global asmCode

    if len(asmCode.code[currentScope][currentBlock]) == 0 or not asmCode.code[currentScope][currentBlock][-1][0] == 'jmp':#If there is a jump at the end of the block, we don't need to add another one This is for return statements in loops
        asmCode.addLine(currentScope, currentBlock, ['jmp', codeLine[0]])


#Sets up for multiple if statement conditionals
def _multipleIfShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    register = currentRegister.getRegister()

    if re.match(cc.numbers, codeLine[1]):
        asmCode.addLine(currentScope, currentBlock, ["mov", register, codeLine[1]])
    else:
        asmCode.addLine(currentScope, currentBlock, ["mov", register, '[' + codeLine[1] + "]"])
    
    jumpExpression = jumpTable[codeLine[2]]

    if re.match(cc.numbers, codeLine[3]):
        asmCode.addLine(currentScope, currentBlock, ["cmp", register, codeLine[3]])
    else:
        secondRegister = currentRegister.getRegister()
        asmCode.addLine(currentScope, currentBlock, ["mov", secondRegister, '[' + codeLine[3] + "]"])
        asmCode.addLine(currentScope, currentBlock, ["cmp", register, secondRegister])
    
    asmCode.addLine(currentScope, currentBlock, [jumpExpression, 'REPLACE'])#We leave this like this so we can change it later


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
        if len(line) > 1:
            if line[1] == 'REPLACE':
                if operator == 'or' and firstConditional == False:#We only change the first conditional of an or statement
                    oppositeJump = oppositeJumps[line[0]]
                    newFinalJump = currentBlock[:1] + str(int(currentBlock[1:]) + 1) 
                    tempLine = oppositeJump + ' ' + newFinalJump
                else:
                    tempLine = line[0] + jumpEnd

                if firstConditional == False:
                    firstConditional = True

                newAsmBlock.append(tempLine)
            else:
                newAsmBlock.append(line)
        else:
            newAsmBlock.append(line)


    asmCode.code[currentScope][currentBlock] = newAsmBlock