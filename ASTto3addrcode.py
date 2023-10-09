'''
-@author: Tyler Ray
-@date: 10/5/2023

- Will take a given AST and convert it to 3 address code
- ***WORK IN PROGRESS***
'''

import re

allowedTypes = r'double|int|float|char|string|signed|unsigned|long|short|void'
typeModifiers = r'signed|unsigned|long|short'
exprOps = r'\+|\-|\/|\*'
relationalOps = r'\<|\>|\<=|\>=|\==|\!='

global threeAddressCode

#The representation of the 3 address code will be a dictionary within dictionaries
threeAddressCode = {} 
global symbolTable

global temporaryIndexCounter
temporaryIndexCounter = 0

global functionScope
functionScope = 'global'

global blockIndicator
blockIndicator = None

global addrIndex
addrIndex = 0


#Our main function
def converter(AST, SymbolTable):
    global threeAddressCode
    global symbolTable 

    symbolTable = SymbolTable

    declList = AST.return_children() #Grabbing the decl list node

    eachDecl = declList[0].return_children() #Grabbing each individual decleration.

    _iteratingThroughMainDecls(eachDecl)

    return threeAddressCode;


#------ Inward Facing modules

def _iteratingThroughMainDecls(eachDecl):
    for decl in eachDecl:
        _iteratingThroughDecl(decl)

def _iteratingThroughDecl(decl):
    global threeAddressCode
    global functionScope
    global blockIndicator

    children = decl.return_children()
    for child in children:
        childValue = child.return_value()

        if childValue == 'id':
            _createFunctionInAddressCode(child)
        elif childValue == 'type':
            pass
        elif childValue == 'Args':
            pass
        elif childValue == 'local_decls':
            threeAddressCode[functionScope][blockIndicator] = {}
            _create3AddressCodeForLocalDecls(child)
        elif childValue == 'stmtList':
            _create3AddressCodeForStmts(child)


def _createFunctionInAddressCode(idNode):
    global threeAddressCode
    global functionScope
    global blockIndicator

    idName = idNode.return_children()[0]
    idName = idName.return_value()

    if len(idNode.return_children()) > 1:
        threeAddressCode[idName] = idNode.return_children()[1].return_value()
    else:
        threeAddressCode[idName] = {}
        functionScope = idName
        blockIndicator = 'L0'
        threeAddressCode[functionScope][blockIndicator] = {}


def _create3AddressCodeForArgs(argsNode):
    global threeAddressCode
    global functionScope
    global addrIndex
    global blockIndicator

    temporaryDict = {}

    args = argsNode.return_children()

    args = list(reversed(args)) # To get the order correct

    for arg in args:
        argID = arg.return_children()
        if isinstance(argID, list) and argID != []:
            argTypeValue = arg.return_value()
            argIDValue = argID[0].return_value()

            temporaryDict[addrIndex] = [argIDValue, 'param', argTypeValue] #We are just going to set the value to param. When we print it out, it will be the param and then the id. But we can't use param as multiple keys
            addrIndex += 1

    threeAddressCode[functionScope][blockIndicator] = temporaryDict

def  _create3AddressCodeForLocalDecls(localDeclsNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    temporaryDict = {}
    localDecls = localDeclsNode.return_children()

    localDecls = list(reversed(localDecls)) # To get the order correct

    for decl in localDecls:
       temporaryDict.update(_create3AddressCodeForDecl(decl, temporaryDict))

    threeAddressCode[functionScope][blockIndicator].update(temporaryDict)


def _create3AddressCodeForDecl(declNode, temporaryDict):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    declChildren = declNode.return_children()

    declID = declNode.return_value()

    declValue = ''
    index = 0
    for child in declChildren:
        childValue = child.return_value()

        if (re.match(allowedTypes, childValue) or re.match(typeModifiers, childValue[:-1])) and index == 0:
            declType = childValue
            
        elif (re.match(allowedTypes, childValue) or re.match(typeModifiers, childValue[:-1])) and index == 1:#Chekcing to see if there is a typemodifier
            declType += ' ' + childValue
            
        elif child.return_children() == []:#Is it just a literal or a expression?
            declValue = childValue
        else:
            exprDict = {}
            exprDict, temporaryvariableName = _create3AddressCodeForExpr(child, exprDict)
            declValue = temporaryvariableName
            temporaryDict.update(exprDict)

            keys = sorted(temporaryDict.keys())
            values = {key: temporaryDict[key] for key in keys}
            temporaryDict = values

        index += 1

    temporaryDict[addrIndex] = [declID, declValue, declType, 'decl']
    addrIndex += 1
    
    return temporaryDict

#Creates the 3 address code for expressions
def _create3AddressCodeForExpr(exprNode, temporaryDict):
    global threeAddressCode
    global functionScope
    global addrIndex

    exprChildren = exprNode.return_children()
    index = 0
    second_exprValue = None
    first_exprValue = None

    temporaryvariableName1 = None
    temporaryvariableName2 = None

    for child in exprChildren:
        childValue = child.return_value()
        if (re.match(exprOps, childValue) or childValue == '()') and index == 0:
            temporaryDict, temporaryvariableName1 = _create3AddressCodeForExpr(child, temporaryDict)
        
        elif (re.match(exprOps, childValue) or childValue == '()') and index == 1:
            temporaryDict, temporaryvariableName2 = _create3AddressCodeForExpr(child, temporaryDict)

        elif child.return_children() == [] and index == 0:
            first_exprValue = childValue

        elif child.return_children() == [] and index == 1:
            second_exprValue = childValue

        index += 1

    
    if exprNode.return_value() != '()':
        if second_exprValue == None and first_exprValue == None:
            second_exprValue = temporaryvariableName1
            first_exprValue = temporaryvariableName2
        
        elif second_exprValue == None:
            if temporaryvariableName1 == None:
                second_exprValue = temporaryvariableName2
            elif temporaryvariableName2 == None:
                second_exprValue = temporaryvariableName1

        if first_exprValue == None:
            if temporaryvariableName1 == None:
                first_exprValue = temporaryvariableName2
            elif temporaryvariableName2 == None:
                first_exprValue = temporaryvariableName1
    
    temporaryvariableName = _createTemporaryVariableName()

    operation = exprNode.return_value()

    if second_exprValue == None and first_exprValue == None:
        if temporaryvariableName1 == None:
            first_exprValue = temporaryvariableName2
        else:
            first_exprValue = temporaryvariableName1
    
    if operation == '()':
        expr_string = '(' + first_exprValue + ')'
    else:
        expr_string = first_exprValue + ' ' + operation + ' ' + second_exprValue

    temporaryDict[addrIndex] = [temporaryvariableName + ' = ' + expr_string, 'expr']
    addrIndex += 1

    return temporaryDict, temporaryvariableName

#Creates temporary variable names for the 3 address code
def _createTemporaryVariableName():
    global temporaryIndexCounter
    temporaryIndexCounter += 1
    return 't' + str(temporaryIndexCounter)


def _create3AddressCodeForStmts(stmtListNode):
    global threeAddressCode
    stmtListChildren = stmtListNode.return_children()

    for stmt in stmtListChildren:
        stmtValue = stmt.return_value()
        if stmtValue == 'if':
            _create3AddressCodeForIfStmt(stmt)
        elif stmtValue == 'while':
            _create3AddressCodeForWhileStmt(stmt)
        elif stmtValue == 'return':
            _create3AddressCodeForReturnStmt(stmt)
        elif stmtValue == 'functionCall':
            _create3AddressCodeForFunctionCall(stmt)
        else:#It is a identifier.
            _create3AddressCodeForAssignStmt(stmt)
    pass

def _create3AddressCodeForIfStmt(ifStmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex
    temporaryDict = {}
    ifStmtChildren = ifStmtNode.return_children()

    for stmt in ifStmtChildren:
        stmtValue = stmt.return_value()
        if stmtValue == '()':
            if threeAddressCode[functionScope][blockIndicator] != {}:
                blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
                threeAddressCode[functionScope][blockIndicator] = {}

            temporaryDict = _create3AddressCodeForstmtParens(stmt)
            index = 0
            for val in list(temporaryDict):
                index += 1
                if temporaryDict[val][0] != 'if':
                    threeAddressCode[functionScope][blockIndicator][val] = temporaryDict[val]
                elif index == len(temporaryDict):
                    threeAddressCode[functionScope][blockIndicator][val] = temporaryDict[val]

        elif stmtValue == '{ }':
            stmtListNode = stmt.return_children()[0]
            blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1) #Adding one to our block indicator
            threeAddressCode[functionScope][blockIndicator] = {}

            _create3AddressCodeForStmts(stmtListNode)

            blockIndicatorForIfStmts = blockIndicator

            blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1) #Adding one to our block indicator
            threeAddressCode[functionScope][blockIndicator] = {}

        elif stmtValue == 'else':
            bracketNode = stmt.return_children()[0]
            stmtListNode = bracketNode.return_children()[0]

            threeAddressCode[functionScope][blockIndicator] = {}
            _create3AddressCodeForStmts(stmtListNode)

            threeAddressCode[functionScope][blockIndicatorForIfStmts][addrIndex] = ['goto L' + str(int(blockIndicator[1:]) + 1), "goto"]

            blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
            threeAddressCode[functionScope][blockIndicator] = {}

def _create3AddressCodeForstmtParens(parenNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    temporaryDict = {}
    parenChildren = parenNode.return_children()

    for operator in parenChildren:
        operatorValue = operator.return_value()

        if re.match(relationalOps, operatorValue):
            temporaryDict.update(_parseRelOpSides(operator))

        elif operatorValue == '||' or operatorValue == '&&':
            temporaryDict = _create3AddressCodeForstmtParens(operator)
            temporaryDict = _create3AddrForMultipleRelOps(temporaryDict)
            temporaryDict[addrIndex] = ['if', temporaryDict[addrIndex - 2][0], operatorValue, temporaryDict[addrIndex - 1][0], temporaryDict[addrIndex-3][4]]

            addrIndex += 1

    return temporaryDict        

#We are removing the previous to if statements. This is allowed when there is only one if, but if we have a relop we want to get rid of them
def _cleaningUpDict(temporaryDict):
    global addrIndex
    temporaryIndex = addrIndex
    for val in list(temporaryDict):
        if temporaryDict[val][0] == 'if' and val != temporaryIndex:
            temporaryDict.pop(val)
            addrIndex -= 1
    temporaryDict = _renumberingDict(temporaryDict)
    return temporaryDict

def _renumberingDict(temporaryDict):
    global addrIndex
    keys = list(temporaryDict.keys())
    for i in range(len(keys)):
        if keys[i] != i:
            temporaryDict[i] = temporaryDict.pop(keys[i])
    addrIndex = len(temporaryDict) -1
    return temporaryDict

def _create3AddrForMultipleRelOps(temporaryDict):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    for val in list(temporaryDict):
        if temporaryDict[val][0] == 'if':
            tempName = _createTemporaryVariableName()
            temporaryDict[addrIndex] = [tempName, str(temporaryDict[val][1]) + ' ' + str(temporaryDict[val][2]) + ' ' + str(temporaryDict[val][3]), 'assign']
            addrIndex += 1

    return temporaryDict

def _parseRelOpSides(operator):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    operatorChildren = operator.return_children()
    temporaryDict = {}
    index = 0
    secondExpr = None
    firstExpr = None

    for child in operatorChildren:
        if child.return_children() != []:
            exprDict = {}
            exprDict, temporaryvariableName = _create3AddressCodeForExpr(child, exprDict)
            if index == 0:
                firstExpr = temporaryvariableName
            else:
                secondExpr = temporaryvariableName
            temporaryDict.update(exprDict)
        else:
            if index == 0:
                firstExpr = child.return_value()
            else:
                secondExpr = child.return_value()
        index += 1

    
    temporaryDict[addrIndex] = ['if', firstExpr, operator.return_value(), secondExpr, 'goto L' + str(int(blockIndicator[1:]) + 1) + ', else goto L' + str(int(blockIndicator[1:]) + 2)]
    addrIndex += 1

    return temporaryDict


def _create3AddressCodeForWhileStmt(whileStmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    children = whileStmtNode.return_children()

    for child in children:
        childValue = child.return_value()

        if childValue == '()':
            if threeAddressCode[functionScope][blockIndicator] != {}:
                blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
                threeAddressCode[functionScope][blockIndicator] = {}

            temporaryDict = _create3AddressCodeForstmtParens(child)
            for val in list(temporaryDict):
                if temporaryDict[val][0] != 'if':
                    threeAddressCode[functionScope][blockIndicator].update(temporaryDict[val])
                else:
                    addrIndexForWhile = addrIndex-1
                    blockAddressForWhile = blockIndicator
                    threeAddressCode[functionScope][blockIndicator] = {}
                    threeAddressCode[functionScope][blockIndicator][val] = temporaryDict[val]

        elif childValue == '{ }':
            stmtListNode = child.return_children()[0]

            blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
            threeAddressCode[functionScope][blockIndicator] = {}

            _create3AddressCodeForStmts(stmtListNode)

            threeAddressCode[functionScope][blockIndicator][addrIndex] = ['goto L' + blockAddressForWhile[1:], "goto"]
            addrIndex += 1

            threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile] = ['if'
                                                                                        ,threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile][1]
                                                                                        ,threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile][2]
                                                                                        ,threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile][3]
                                                                                        ,threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile][4][0:7] + ', else goto L' + str(int(blockIndicator[1:]) + 1)]

            blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
            threeAddressCode[functionScope][blockIndicator] = {}

        

def _create3AddressCodeForReturnStmt(returnStmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    temporaryDict = {}
    returnStmtChildren = returnStmtNode.return_children()

    child = returnStmtChildren[0]

    if child.return_children() != []:
        exprDict = {}
        exprDict, temporaryvariableName = _create3AddressCodeForExpr(child, exprDict)
        declValue = temporaryvariableName
        temporaryDict.update(exprDict)
        temporaryDict[addrIndex] = [declValue, 'return']
        addrIndex += 1
        
    else:
        declValue = child.return_value()
        temporaryDict[addrIndex] = [declValue, 'return']
        addrIndex += 1

    threeAddressCode[functionScope][blockIndicator].update(temporaryDict) 

def _create3AddressCodeForFunctionCall(stmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    stmtChildren = stmtNode.return_children()
    functionID = stmtChildren[0].return_value()
    functionIDChildren = stmtChildren[0].return_children()

    args = ''
    for child in functionIDChildren:
        args += child.return_value() + ', '

    args = args[:-2]
    threeAddressCode[functionScope][blockIndicator][addrIndex] = [functionID, args, 'functionCall']
    addrIndex += 1



def _create3AddressCodeForAssignStmt(assignStmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    temporaryDict = {}
    assignStmtChildren = assignStmtNode.return_children()
    declID = assignStmtNode.return_value()

    child = assignStmtChildren[0]
    if child.return_children() == []: 
        declValue = child.return_value()
        temporaryDict[addrIndex] = [declID, declValue, 'assign']
        addrIndex += 1      
    
    elif child.return_value() == '*' or child.return_value() == '&':
        secondchild = child.return_children()[0]
        declValue = child.return_value() + secondchild.return_value()
        temporaryDict[addrIndex] = [declID, declValue, 'assign']
        addrIndex += 1
    else:
        exprDict = {}
        exprDict, temporaryvariableName = _create3AddressCodeForExpr(child, exprDict)
        declValue = temporaryvariableName
        temporaryDict.update(exprDict)
        temporaryDict[addrIndex] = [declID, declValue, 'assign']
        addrIndex += 1
        
   
    threeAddressCode[functionScope][blockIndicator].update(temporaryDict)
    