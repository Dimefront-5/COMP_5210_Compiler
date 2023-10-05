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

global threeAddressCode

#the representation of the 3 address code will be a dictionary within dictionaries
#Example: = {'main': {L1: {1: j = 5/6, 2: k = 7+8}, L2: {1: j = 5/6, 2: k = 7+8, etc...}}
threeAddressCode = {} 
global symbolTable

global temporaryIndexCounter
temporaryIndexCounter = 0

global functionScope
functionScope = 'global'

global blockIndicator
blockIndicator = None


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
    children = decl.return_children()
    for child in children:
        childValue = child.return_value()

        if childValue == 'id':
            _createFunctionInAddressCode(child)
        elif childValue == 'type':
            pass
        elif childValue == 'Args':
            _create3AddressCodeForArgs(child)
        elif childValue == 'local_decls':
            _create3AddressCodeForLocalDecls(child)
        elif childValue == 'stmtList':
            _create3AddressCodeForStmts(child)


def _createFunctionInAddressCode(idNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    idName = idNode.return_children()[0]
    idName = idName.return_value()

    threeAddressCode[idName] = {}
    functionScope = idName
    blockIndicator = 'L0'


def _create3AddressCodeForArgs(argsNode):
    global threeAddressCode
    global functionScope
    temporaryDict = {}

    args = argsNode.return_children()

    for arg in args:
        argID = arg.return_children()
        if isinstance(argID, list) and argID != []:
            argTypeValue = arg.return_value()
            argIDValue = argID[0].return_value()

            temporaryDict[argIDValue] = ['param', argTypeValue] #We are just going to set the value to param. When we print it out, it will be the param and then the id. But we can't use param as multiple keys

    threeAddressCode[functionScope][blockIndicator] = dict(reversed(temporaryDict.items())) #Reversing the dictionary so that the order is correct

def  _create3AddressCodeForLocalDecls(localDeclsNode):
    global threeAddressCode
    global functionScope

    temporaryDict = {}
    localDecls = localDeclsNode.return_children()

    for decl in localDecls:
       _create3AddressCodeForDecl(decl, temporaryDict)

    threeAddressCode[functionScope][blockIndicator].update(dict(reversed(temporaryDict.items()))) #Reversing the dictionary so that the order is correct


def _create3AddressCodeForDecl(declNode, temporaryDict):
    global threeAddressCode
    global functionScope

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
            temporaryDict[declID] = [declValue, declType, 'decl']
            temporaryDict.update(dict(reversed(exprDict.items())))

        index += 1

    temporaryDict[declID] = [declValue, declType, 'decl']

#Creates the 3 address code for expressions
def _create3AddressCodeForExpr(exprNode, temporaryDict):
    global threeAddressCode
    global functionScope
    exprChildren = exprNode.return_children()
    index = 0
    second_exprValue = None
    first_exprValue = None

    for child in exprChildren:
        childValue = child.return_value()

        if re.match(exprOps, childValue):
            temporaryDict, temporaryvariableName = _create3AddressCodeForExpr(child, temporaryDict)

        elif child.return_children() == [] and index == 0:
            first_exprValue = childValue

        elif child.return_children() == [] and index == 1:
            second_exprValue = childValue

        index += 1

    if second_exprValue == None:
        second_exprValue = temporaryvariableName

    if first_exprValue == None:
        first_exprValue = temporaryvariableName
    
    temporaryvariableName = _createTemporaryVariableName()

    operation = exprNode.return_value()

    expr_string = first_exprValue + ' ' + operation + ' ' + second_exprValue

    temporaryDict[temporaryvariableName] = [expr_string, 'expr']

    return temporaryDict, temporaryvariableName

#Creates temporary variable names for the 3 address code
def _createTemporaryVariableName():
    global temporaryIndexCounter
    temporaryIndexCounter += 1
    return 't' + str(temporaryIndexCounter)


def _create3AddressCodeForStmts(stmtListNode):
    stmtListChildren = stmtListNode.return_children()

    for stmt in stmtListChildren:
        stmtValue = stmt.return_value()
        if stmtValue == 'if':
            pass
        elif stmtValue == 'while':
            pass
        elif stmtValue == 'return':
            pass
        else:#It is a identifier.
            _create3AddressCodeForAssignStmt(stmt)
    pass

def _create3AddressCodeForIfStmt(ifStmtNode):
    pass

def _create3AddressCodeForWhileStmt(whileStmtNode):
    pass

def _create3AddressCodeForReturnStmt(returnStmtNode):
    pass

def _create3AddressCodeForAssignStmt(assignStmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator

    temporaryDict = {}
    assignStmtChildren = assignStmtNode.return_children()
    declID = assignStmtNode.return_value()

    child = assignStmtChildren[0]
    if child.return_children() != []:
        exprDict = {}
        exprDict, temporaryvariableName = _create3AddressCodeForExpr(child, exprDict)
        declValue = temporaryvariableName
        temporaryDict[declID] = [declValue, 'assign']
        temporaryDict.update(dict(reversed(exprDict.items())))
    else:
        declValue = child.return_value()
        temporaryDict[declID] = [declValue, 'assign']

    threeAddressCode[functionScope][blockIndicator].update(temporaryDict) #Reversing the dictionary so that the order is correct
    