'''
-@author: Tyler Ray
-@date: 12/3/2023

- This file will convert our optimized 3 address code into assembly code
- '''

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
                output += ' ' * indent + '.' + scope + '\n'
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

global registerMapping

global variableMapping

def codeShaper(threeAddrCode, symbolTable):
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
            _createPrelude(symbolTable, threeAddrCode)

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
    
    _registrySetter()

    _changingMemoryReferences(symbolTable)

    recreatedASMCode = _recreatingCode(symbolTable)
    
    return recreatedASMCode



#Creates our prelude for when we start a function
def _createPrelude(symbolTable, threeAddrCode):
    global currentScope
    global currentBlock
    global asmCode

    asmCode.addLine(currentScope, currentBlock, ["push", "rbp"])
    asmCode.addLine(currentScope, currentBlock, ["mov", "rbp", "rsp"])
    stackSpaceNeeded = _figureOutHowMuchStackSpaceWeNeed(symbolTable, threeAddrCode)
    asmCode.addLine(currentScope, currentBlock, ["sub", "rsp", str(stackSpaceNeeded)])

#Figures out how much stack space we need for a function
def _figureOutHowMuchStackSpaceWeNeed(symbolTable, threeAddrCode):
    global currentScope
    spaceNeeded = 4

    arguments = symbolTable.get_args(currentScope)
    variables = symbolTable.get_vars(currentScope)

    foundArguments = []
    foundVars = []

    for block in threeAddrCode[currentScope]:
        for key, line in threeAddrCode[currentScope][block].items():
            if len(line) > 1 and line[-1] != 'functionCall':
                newSpace, foundArguments, foundVars = _doesItNeedSpace(line[1], arguments, variables, foundArguments, foundVars)
                spaceNeeded += newSpace

                if len(line) > 2:
                    newSpace, foundArguments, foundVars = _doesItNeedSpace(line[2], arguments, variables, foundArguments, foundVars)
                    spaceNeeded += newSpace

                    if len(line) > 3:
                        newSpace, foundArguments, foundVars = _doesItNeedSpace(line[3], arguments, variables, foundArguments, foundVars)
                        spaceNeeded += newSpace


    return spaceNeeded

def _doesItNeedSpace(value, arguments, variables, foundarguments, foundvars):
    global currentScope
    spaceNeeded = 0
    if value in arguments and not value in foundarguments:
        if arguments[value] == 'int' or arguments[value] == 'char':
            spaceNeeded += 4

        elif arguments[value] == 'float':
            spaceNeeded += 8

        elif arguments[value] == 'double':
            spaceNeeded += 16

        foundarguments.append(value)

    elif value in variables and not value in foundvars:
        if variables[value][0] == 'int' or variables[value][0] == 'char':
            spaceNeeded += 4

        elif variables[value][0] == 'float':
            spaceNeeded += 8

        elif variables[value][0] == 'double':
            spaceNeeded += 16
        
        foundvars.append(value)

    return spaceNeeded, foundarguments, foundvars

#Creates our epilogue for when we close out a function
def _createEpilogue():
    global currentScope
    global currentBlock
    global asmCode

    returnBlock = currentScope + 'Return'

    asmCode.addBlock(currentScope, returnBlock)#We add a block for our return statement so if there are any other returns in the code they can jump straight to it
    asmCode.addLine(currentScope, returnBlock, ["leave"])
    asmCode.addLine(currentScope, returnBlock, ["ret"])


#Shapes each functions code into assembly
def _codeShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister


    statementIndicator = codeLine[-1]
    statementIndicatorForIfs = codeLine[0] #I don't know why I did this, but for some reason I left its at the front. It makes it look nice while debugging but not for consistency.
    
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
        returnCode = ["mov", "rax", f'{int(codeLine[0]):x}h']
    elif codeLine[0][0] == '\'' or codeLine[0][0] == '\"':  #For characters
        returnCode = ["mov", "rax", format(ord(codeLine[0][1]), 'x') + "h"]
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
        if codeLine[1].isnumeric():
            asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", f'{int(codeLine[1]):x}h' ])
        elif codeLine[1][0] == '\'' or codeLine[1][0] == '\"':  #For characters
            asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", format(ord(codeLine[1][1]), 'x') + "h"])
        else:
            register = currentRegister.getRegister()

            _movAdder(codeLine[1], register)
            asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", register])

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

#Sets up for multiple if statement conditionals
def _multipleIfShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    register = currentRegister.getRegister()

    _movAdder(codeLine[1], register)
    
    jumpExpression = jumpTable[codeLine[2]]

    _secondInstructionBlockShaper("cmp", register, codeLine[3])
    
    asmCode.addLine(currentScope, currentBlock, [jumpExpression, 'REPLACE'])#We leave this like this so we can change it later

#Will check for some basic optimizations for multiplication and division
#Then will see if we can shift it instead of using the actual operation
def _shiftChecking(codeLine, operation):
    if codeLine[1] == '1':#If we are multiplying by 1, we can just move the number into the variable
        asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", f'{int(codeLine[3]):x}h'])

    elif codeLine[3] == '1':
        asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", f'{int(codeLine[1]):x}h'])

    elif codeLine[1] == '0':#we can just move 0 into the variable
        asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", '0h'])

    elif codeLine[1].isnumeric() and _powerFinder(int(codeLine[1])):
        if operation == 'div':
            _shiftAdder(codeLine, 1, 3, 'right')
        else:
            _shiftAdder(codeLine, 1, 3, 'left')

    elif codeLine[3].isnumeric() and _powerFinder(int(codeLine[3])):#If we are dividing by an even number, we can just shift the number to the left
        if operation == 'div':
            _shiftAdder(codeLine, 3, 1, 'right')
        else:
            _shiftAdder(codeLine, 3, 1, 'left')
    else:
        _operatorShaper(codeLine, operation)

#I had ChatGPT generate this function for me
def _powerFinder(num):
    # Check if the number is greater than 0 and has only one bit set to 1.
    # A power of 2 in binary has only one bit set.
    return num > 0 and (num & (num - 1)) == 0


#Looks to see if we can use shifts instead of the actual operation
def _shiftAdder(codeLine, codeLineIndex, oppositeIndex, direction):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    shiftNumber = _getShiftCount(int(codeLine[codeLineIndex]))
    register = currentRegister.getRegister()

    _movAdder(codeLine[oppositeIndex], register)

    if direction == 'left':
        asmCode.addLine(currentScope, currentBlock, ["shl", register , f'{shiftNumber:x}h'])
    else:
        asmCode.addLine(currentScope, currentBlock, ["shr" ,register, f'{shiftNumber:x}h'])

    asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", register])


#I had ChatGPT generate this function for me
def _getShiftCount(num):
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

    _movAdder(codeLine[1], register)
    
    _secondInstructionBlockShaper(instruction, register, codeLine[3])

    asmCode.addLine(currentScope, currentBlock, ["mov", "[" + codeLine[0] + "]", register])

def _movAdder(value, register):
    global currentScope
    global currentBlock
    global asmCode


    if re.match(cc.numbers, value):
        asmCode.addLine(currentScope, currentBlock, ["mov", register, f'{int(value):x}h'])
    
    elif value[0:2] == '0x':
        asmCode.addLine(currentScope, currentBlock, ["mov", register, f'{int(value):x}h'])

    elif value[0] == '\'' or value[0] == '\"':
        asmCode.addLine(currentScope, currentBlock, ["mov", register, format(ord(value[1]), 'x') + 'h'])
    
    else:
        asmCode.addLine(currentScope, currentBlock, ["mov", register, '[' + value + "]"])

def _secondInstructionBlockShaper(operation, register1, value):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    if re.match(cc.numbers, value):
        asmCode.addLine(currentScope, currentBlock, [operation, register1, f'{int(value):x}h'])
    elif value[0:2] == '0x':
        asmCode.addLine(currentScope, currentBlock, [operation, register1, f'{value[2:]}h'])
    elif value[0] == '\'' or value[0] == '\"':
        asmCode.addLine(currentScope, currentBlock, [operation, register1, format(ord(value[1]), 'x') + 'h'])
    else:
        register2 = currentRegister.getRegister()
        asmCode.addLine(currentScope, currentBlock, ['mov', register2, '[' + value + "]"])
        asmCode.addLine(currentScope, currentBlock, [operation, register1, register2])


#shapes our call statements
def _callShaper(codeLine):
    global currentScope
    global currentBlock
    global currentRegister
    global asmCode

    for argument in codeLine[1]:
        if re.match(cc.numbers, argument):
            asmCode.addLine(currentScope, currentBlock, ["push", f'{int(argument):x}h'])
        elif argument[0] == '\'' or argument[0] == '\"':
            asmCode.addLine(currentScope, currentBlock, ["push", format(ord(argument[1]), 'x') + 'h'])
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

        _movAdder(codeLine[1], register)
        
        _secondInstructionBlockShaper("cmp", register, codeLine[3])
        
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
                    tempLine = [oppositeJump, newFinalJump]
                else:
                    tempLine = [line[0], jumpEnd]

                if firstConditional == False:
                    firstConditional = True

                newAsmBlock.append(tempLine)
            else:
                newAsmBlock.append(line)
        else:
            newAsmBlock.append(line)


    asmCode.code[currentScope][currentBlock] = newAsmBlock


#Adds our global variables to the assembly code
def _addingGlobalVars(symbolTable):
    global_vars = symbolTable.get_vars('global')

    for var in global_vars:
        asmCode.addBlock('global', var)
        if global_vars[var][0] == 'int' or global_vars[var][0] == 'float' or global_vars[var][0] == 'double':
            if len(global_vars[var]) > 1:
                asmCode.addLine('global', var, [f'.long',f'{global_vars[var][1]}h'])
            else:
                asmCode.addLine('global', var, ['.long', 0])

        elif global_vars[var][0] == 'char':
            if len(global_vars[var]) > 1:
                byteValue = format(ord(global_vars[var][1][1]), 'x') + 'h'
                asmCode.addLine('global', var, [f'.byte', f'{byteValue}'])
            else:
                asmCode.addLine('global', var, ['.byte', 0])

#Creates a new mapping for our registers
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

    _registerAllocator(registersInBlock)

#Allocates registers to our code
def _registerAllocator(registersInBlock):
    global registerMapping
    registerMapping = {}

    for block in registersInBlock:
        registerMapping[block] = {}

        registerList = ['rax', 'rbx', 'rcx', 'rdx', 'rsi', 'rdi', 'r8', 'r9', 'r10', 'r11', 'r12', 'r13', 'r14', 'r15']
        registerCount = len(registerList)
        index = -1
        for register in registersInBlock[block]:#I am just going to assign registers in the order they appear in the code, I won't leave values in registers.
            index = (index + 1) % registerCount
            registerMapping[block][register] = registerList[index]                          

#Will assign refrences to our variables in the stack
def _changingMemoryReferences(symbolTable):
    global variableMapping

    stackAddress = 4
    variableMapping = {}
    for scope in symbolTable.symbolTable:
        variableMapping[scope] = {}
        if scope != 'global':
            variables = symbolTable.get_vars(scope)
            arguments = symbolTable.get_args(scope)

            for variable in variables:
                if variables[variable][0] == 'int':
                    variableMapping[scope][variable] = f'DWORD PTR [rbp-{stackAddress}]'
                    stackAddress += 4
                elif variables[variable][0] == 'char':#We used to put the value in the symbol table so thats why there is a 0 here
                    variableMapping[scope][variable] = f'BYTE PTR [rbp-{stackAddress}]'
                    stackAddress += 4
                elif variables[variable][0] == 'float':
                    variableMapping[scope][variable] = f'QWORD PTR [rbp-{stackAddress}]'
                    stackAddress += 8
                elif variables[variable][0] == 'double':
                    variableMapping[scope][variable] = f'QWORD PTR [rbp-{stackAddress}]'
                    stackAddress += 16

            argumentAddress = 4
            for argument in reversed(arguments): #Needs to be reversed so we can access the arguments in the correct order
                if arguments[argument] == 'int' or arguments[argument] == 'char':#We don't put the number the argument is at in the symbol table anymore, so we don't need to check for it
                    if arguments[argument] == 'char':
                        variableMapping[scope][f'{argument}'] = f'BYTE PTR [rbp+{argumentAddress}]'
                    else:
                        variableMapping[scope][argument]= f'DWORD PTR [rbp+{argumentAddress}]'
                    argumentAddress += 4
                elif arguments[argument] == 'float':
                    variableMapping[scope][argument] = f'QWORD PTR [rbp+{argumentAddress}]'
                    argumentAddress += 8
                elif arguments[argument] == 'double':
                    variableMapping[scope][argument]= f'QWORD PTR [rbp+{argumentAddress}]'
                    argumentAddress += 16


#Will recreate our assembly code with the new mappings and memory references
def _recreatingCode(symbolTable):
    global asmCode
    global currentScope
    global currentBlock

    newAsmCode = assemblyCode()

    temporaryVariables = {}

    currentTemporaryVariable = ''

    for scope in asmCode.code:
        newAsmCode.addScope(scope)
        currentScope = scope
        for block in asmCode.code[scope]:
            currentBlock = block
            newAsmCode.addBlock(scope, block)
            newAsmCode = _lookingThroughLines(symbolTable, newAsmCode, temporaryVariables, currentTemporaryVariable)

    return newAsmCode

#Walks through each line to see if we can change any of the temporary variables to the correct registers or memory references
def _lookingThroughLines(symbolTable, newAsmCode, temporaryVariables, currentTemporaryVariable):
    global currentScope
    global currentBlock
    global asmCode
    global registerMapping
    global variableMapping

    dontAddLine = False
    for line in asmCode.code[currentScope][currentBlock]:

        if currentTemporaryVariable != '':
            newAsmCode, temporaryVariables, currentTemporaryVariable, dontAddLine = _changingTempVars(symbolTable, newAsmCode, temporaryVariables, currentTemporaryVariable, line)

        elif len(line) > 1:
            line, currentTemporaryVariable, dontAddLine = _isThisARegisterOrAMemoryReference(line, 1, dontAddLine)
                                   
            if len(line) > 2:
                line, currentTemporaryVariable, dontAddLine = _isThisARegisterOrAMemoryReference(line, 2, dontAddLine)
                
                if currentTemporaryVariable != '':
                    temporaryVariables[currentTemporaryVariable].append(line[1])

            if dontAddLine != True:
                newAsmCode.addLine(currentScope, currentBlock, line)

            elif currentTemporaryVariable == '':
                temporaryVariables[line[1][1:-1]] = [line[2]]

        else:
            newAsmCode.addLine(currentScope, currentBlock, line)

    return newAsmCode

#Seeing if our line contains a register or a memory reference
def _isThisARegisterOrAMemoryReference(line, index, dontAddLine):
    global currentScope
    global currentBlock
    global asmCode
    global registerMapping
    global variableMapping

    currentTemporaryVariable = ''
    if _isItARegister(line[index], registerMapping, currentBlock) == True:
        line[index] = registerMapping[currentBlock][line[index]]

    if line[index][:1] == '[' and line[index][-1:] == ']':
        if line[index][1:-1] in variableMapping[currentScope]:
            line[index] = variableMapping[currentScope][line[index][1:-1]]

        elif 'global' in asmCode.code and line[index][1:-1] in asmCode.code['global']:
            line[index] = line[index][1:-1] + '[' + 'rip' + ']'
                
        else:#if it is a temporary variable
            dontAddLine = True
            if index == 2:
                currentTemporaryVariable = line[index][1:-1]
    
    return line, currentTemporaryVariable, dontAddLine


#Checks to see if a line is a register
def _isItARegister(line, newMappings, block):
    if line[:1] == 'r' and line[1:].isnumeric():
        if line in newMappings[block]:
            return True
    return False

#Changes our temporary variables to the correct registers and memory references and removes the temp variables from the code
def _changingTempVars(symbolTable, newAsmCode, temporaryVariables, currentTemporaryVariable, line):
    temp = currentTemporaryVariable
    
    currentTemporaryVariable, dontAddLine, newAsmCode, temporaryVariables = _replacingTempVars(temporaryVariables, line, newAsmCode, currentTemporaryVariable, symbolTable)
    
    if temp != currentTemporaryVariable:#If we are no longer using the same temporary variable, we need to add the line that we were working on
        currentTemporaryVariable = ''
        dontAddLine = False

    return newAsmCode,temporaryVariables, currentTemporaryVariable, dontAddLine

#Replaces our temporary variables with the correct registers and memory references
def _replacingTempVars(temporaryVariables, line, newAsmCode, currentTemporaryVariable, symbolTable):   
    global currentScope
    global currentBlock
    global registerMapping
    global variableMapping
    
    if len(line) < 3:#If we ever have a return or a leave or a goto
        newAsmCode.addLine(currentScope, currentBlock, line)
        return '', False, newAsmCode, temporaryVariables
    
    destination = line[1]
    source = line[2]

    if source in registerMapping[currentBlock] and destination not in registerMapping[currentBlock]: #is the destination not a register and is line[2] a register
        return _remappingSourceRegisters(line, temporaryVariables, currentTemporaryVariable, newAsmCode, symbolTable)
                
    elif source in registerMapping[currentBlock] and destination in registerMapping[currentBlock]: #are they both registers?
        line = _remappingBothRegisters(line, temporaryVariables, currentTemporaryVariable)
        newAsmCode.addLine(currentScope, currentBlock, line)
        return currentTemporaryVariable, True, newAsmCode, temporaryVariables

    elif destination in registerMapping[currentBlock]:#Is the destination a register?
        newAsmCode = _remappingDestRegisters(line, temporaryVariables, currentTemporaryVariable, newAsmCode)
        
        return currentTemporaryVariable, True, newAsmCode, temporaryVariables

#If the dest register is a temporary variable, we need to change it to the correct register
def _remappingDestRegisters(line, temporaryVariables, currentTemporaryVariable, newAsmCode):
    global currentScope
    global currentBlock
    global registerMapping
    global variableMapping


    destination = line[1]
    source = line[2]

    actualRegister = registerMapping[currentBlock][destination]

    if actualRegister == temporaryVariables[currentTemporaryVariable][1]:#Can the destination register be treated as the temporary variable register
        line[1] = temporaryVariables[currentTemporaryVariable][0]
        newAsmCode.addLine(currentScope, currentBlock, line)
        return newAsmCode
    
    else:
        line[1] = actualRegister
        if source[1:-1] in variableMapping[currentScope]:
            line[2] = variableMapping[currentScope][source[1:-1]]
            
        newAsmCode.addLine(currentScope, currentBlock, line)
        return newAsmCode

#If the source register is a temporary variable, we need to change it to the correct register
def _remappingSourceRegisters(line, temporaryVariables, currentTemporaryVariable, newAsmCode, symbolTable):
    global currentScope
    global currentBlock
    global registerMapping
    global variableMapping

    destination = line[1]
    source = line[2]

    actualRegister = registerMapping[currentBlock][source]

    if actualRegister == temporaryVariables[currentTemporaryVariable][1]:#Is the register a register we can treat as the temporary variable register
        line[2] = temporaryVariables[currentTemporaryVariable][0]
        if destination[1:-1] in symbolTable.get_vars(currentScope) or destination[1:-1] in symbolTable.get_args(currentScope):#If the destination address is a permanent variable we are done fixing temp variables
            line[1] = variableMapping[currentScope][destination[1:-1]]
            newAsmCode.addLine(currentScope, currentBlock, line)
            return '', False, newAsmCode, temporaryVariables

        else:#If it isn't we need to look at the new temporary variable in the code
            currentTemporaryVariable = destination[1:-1]
            temporaryVariables[currentTemporaryVariable]= [source]
            return currentTemporaryVariable, True, newAsmCode, temporaryVariables
        
#If both are registers, (For math and whatnot) we need to change them to the correct registers
def _remappingBothRegisters(line, temporaryVariables, currentTemporaryVariable):
    global currentBlock
    global registerMapping

    destination = line[1]
    source = line[2]

    actualRegister = registerMapping[currentBlock][source]
    secondActualRegister = registerMapping[currentBlock][destination]

    if actualRegister == temporaryVariables[currentTemporaryVariable][1]:#Can the destination register be treated as the temporary variable register
        line[2] = temporaryVariables[currentTemporaryVariable][0]
    else:
        line[2] = actualRegister
    
    if secondActualRegister == temporaryVariables[currentTemporaryVariable][1]:#Can the source register be treated as the temporary variable register
        line[1] = temporaryVariables[currentTemporaryVariable][0]
    else:
        line[1] = secondActualRegister
    
    return line