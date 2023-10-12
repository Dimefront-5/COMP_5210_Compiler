'''
-@author: Tyler Ray
-@date: 10/10/2023

- Will take a given AST and convert it to 3 address code
'''

import re
import compilerconstants as cc

allowedTypes = r'double|int|float|char|string|signed|unsigned|long|short|void'
typeModifiers = r'signed|unsigned|long|short'
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

#Iterates through the main declerations or a program
def _iteratingThroughMainDecls(eachDecl):
    for decl in eachDecl:
        _iteratingThroughDecl(decl)

#Walks through each decl and looks for it's components. 
def _iteratingThroughDecl(decl):
    global threeAddressCode
    global functionScope
    global blockIndicator

    children = decl.return_children()
    for child in children:
        childValue = child.return_value()

        if childValue == 'id':
            _createFunctionInAddressCode(child)
        elif childValue == 'type': #we don't care about the type for 3 address code
            pass
        elif childValue == 'Args': #We don't care about the args for 3 address code, we have already checked that they exist in our parser.
            pass
        elif childValue == 'local_decls':
            threeAddressCode[functionScope][blockIndicator] = {}
            _create3AddressCodeForLocalDecls(child)

        elif childValue == 'stmtList':
            _create3AddressCodeForStmts(child)

#creates our representation of a function within the 3 address code
def _createFunctionInAddressCode(idNode):
    global threeAddressCode
    global functionScope
    global blockIndicator

    idName = idNode.return_children()[0]
    idName = idName.return_value()

    if len(idNode.return_children()) > 1: #If the decleration is a variable, we only have the value returned.
        threeAddressCode[idName] = idNode.return_children()[1].return_value()
    else:#Is it a function?
        threeAddressCode[idName] = {}
        functionScope = idName
        blockIndicator = 'L0'
        threeAddressCode[functionScope][blockIndicator] = {}

#Not currently used, we are going to ignore the args for now
'''
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

    threeAddressCode[functionScope][blockIndicator] = temporaryDict'''

#Walks through each local decl
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

#Will create 3 address code for a decl depending on what it is
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

        if (re.match(allowedTypes, childValue) or re.match(typeModifiers, childValue[:-1])) and index == 0:#Checking for types
            declType = childValue
            
        elif (re.match(allowedTypes, childValue) or re.match(typeModifiers, childValue[:-1])) and index == 1:#Chekcing to see if there is a typemodifier
            declType += ' ' + childValue
            
        elif child.return_children() == []:#Is it just a literal or a expression?
            declValue = childValue
        else:#is our decl value an expression?
            exprDict = {}
            exprDict, temporaryvariableName = _create3AddressCodeForExpr(child, exprDict)
            declValue = temporaryvariableName
            temporaryDict.update(exprDict)

            keys = sorted(temporaryDict.keys())#we want to sort our temporary dict so it appears in order for the 3address code.
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

    #We are going to iterate through and since we want to preserve order of how the expressions appear, we keep track of what index the node is at.
    index = 0
    second_exprValue = None
    first_exprValue = None

    temporaryvariableName1 = None
    temporaryvariableName2 = None

    for child in exprChildren:
        childValue = child.return_value()
        if (re.match(cc.exprOps, childValue) or childValue == '()') and index == 0: #is the next child an expression?
            temporaryDict, temporaryvariableName1 = _create3AddressCodeForExpr(child, temporaryDict)
        
        elif (re.match(cc.exprOps, childValue) or childValue == '()') and index == 1:
            temporaryDict, temporaryvariableName2 = _create3AddressCodeForExpr(child, temporaryDict)

        elif child.return_children() == [] and index == 0:#Is it a literal?
            first_exprValue = childValue

        elif child.return_children() == [] and index == 1:
            second_exprValue = childValue

        index += 1

    
    temporaryDict, temporaryvariableName = _piecingTogetherExpressionCorrectly(exprNode, temporaryDict, second_exprValue, first_exprValue, temporaryvariableName1, temporaryvariableName2)
    
    return temporaryDict, temporaryvariableName

def _piecingTogetherExpressionCorrectly(exprNode, temporaryDict, second_exprValue, first_exprValue, temporaryvariableName1, temporaryvariableName2):
    global addrIndex
    
    #We want to preserve the order so are making sure each value has something in it.
    if exprNode.return_value() != '()':#For parens, we want to do something different, since it will have different children
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
    
    if operation == '()':
        if second_exprValue == None and first_exprValue == None: #Want to make sure first_exprValue has something in it.
            if temporaryvariableName1 == None:
                first_exprValue = temporaryvariableName2
            else:
                first_exprValue = temporaryvariableName1
        temporaryDict[addrIndex] = [temporaryvariableName, first_exprValue, operation, 'assign']
    else:
        temporaryDict[addrIndex] = [temporaryvariableName, first_exprValue, operation, second_exprValue, 'assign']
    addrIndex += 1

    return temporaryDict, temporaryvariableName

#Creates temporary variable names for the 3 address code
def _createTemporaryVariableName():
    global temporaryIndexCounter
    temporaryIndexCounter += 1
    return 't' + str(temporaryIndexCounter)

#Will iterate through stmts and create 3 address code for each stmt
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

#Creates 3 address code for if statements
def _create3AddressCodeForIfStmt(ifStmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex
    temporaryDict = {}
    ifStmtChildren = ifStmtNode.return_children()

    for stmt in ifStmtChildren:
        stmtValue = stmt.return_value()
        if stmtValue == '()': #are we looking through the if expression?

            temporaryDict = _create3AddressCodeForstmtParens(stmt)
            index = 0
            
            for val in list(temporaryDict):
                index += 1
                #print(threeAddressCode[functionScope][blockIndicator])
                if temporaryDict[val][0] != 'if':#While we walk through the code, we will be removing ifs that appear when we are evaluating expressions that have || or &&. We only want the final if statement to show up.
                    threeAddressCode[functionScope][blockIndicator][val] = temporaryDict[val]

                elif index == len(temporaryDict):
                    if threeAddressCode[functionScope][blockIndicator] != {}: #Did the previous block have something in it? If not, we can just overwrite it. and Use it for the if statement. If not, we will create a new block.
                        blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
                        threeAddressCode[functionScope][blockIndicator] = {}

                    threeAddressCode[functionScope][blockIndicator][val] = temporaryDict[val]

        elif stmtValue == '{ }':
            blockIndicatorForIfStmts = _create3AddressCodeForBracketsInIf(stmt)

        elif stmtValue == 'else':
            _create3AddressCodeForElseStmt(stmt, blockIndicatorForIfStmts)

#Creates 3 address code for else statements
def _create3AddressCodeForElseStmt(stmt, blockIndicatorForIfStmts):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    bracketNode = stmt.return_children()[0]
    stmtListNode = bracketNode.return_children()[0]

    threeAddressCode[functionScope][blockIndicator] = {}
    _create3AddressCodeForStmts(stmtListNode)

    threeAddressCode[functionScope][blockIndicatorForIfStmts][addrIndex] = ['goto L' + str(int(blockIndicator[1:]) + 1), "goto"]

    blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
    threeAddressCode[functionScope][blockIndicator] = {}

#Creates 3 address code for brackets in if statements
def _create3AddressCodeForBracketsInIf(stmt):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    stmtListNode = stmt.return_children()[0]
    blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1) #Adding one to our block indicator
    threeAddressCode[functionScope][blockIndicator] = {}

    _create3AddressCodeForStmts(stmtListNode)

    blockIndicatorForIfStmts = blockIndicator

    blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1) #Adding one to our block indicator
    threeAddressCode[functionScope][blockIndicator] = {}
    return blockIndicatorForIfStmts

#Creates 3 address code for the expression in the if statement
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
            temporaryDict[addrIndex] = ['if', temporaryDict[addrIndex - 2][0], operatorValue, temporaryDict[addrIndex - 1][0], temporaryDict[addrIndex-3][4]]#creating a if statement for each expression.

            addrIndex += 1

    return temporaryDict        

#Creates 3 address code for multiple relational operators
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

#Parsing both sides of a relative operator
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
        if child.return_children() != []: #Is it an expression?
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

#Creates 3 address code for while statements
def _create3AddressCodeForWhileStmt(whileStmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    children = whileStmtNode.return_children()

    for child in children:
        childValue = child.return_value()

        if childValue == '()':

            temporaryDict = _create3AddressCodeForstmtParens(child)
            for val in list(temporaryDict):
                if temporaryDict[val][0] != 'if':
                    threeAddressCode[functionScope][blockIndicator][val] = temporaryDict[val]


                else:
                    if threeAddressCode[functionScope][blockIndicator] != {}:#Same as if statement with checking if the previous block had something in it.
                        blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
                        threeAddressCode[functionScope][blockIndicator] = {}

                    addrIndexForWhile = addrIndex-1#We want to know what the address index is for the if statement. We will use this to create the goto statement for the while loop.
                    blockAddressForWhile = blockIndicator #along with block Address
                    threeAddressCode[functionScope][blockIndicator] = {}
                    threeAddressCode[functionScope][blockIndicator][val] = temporaryDict[val]

        elif childValue == '{ }':
            _creating3AddressCodeForBracketsInWhile(child, addrIndexForWhile, blockAddressForWhile)

#Will parse through the brackets in a while loop
def _creating3AddressCodeForBracketsInWhile(child, addrIndexForWhile, blockAddressForWhile):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    stmtListNode = child.return_children()[0]

    blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
    threeAddressCode[functionScope][blockIndicator] = {}

    _create3AddressCodeForStmts(stmtListNode)

    threeAddressCode[functionScope][blockIndicator][addrIndex] = ['goto L' + blockAddressForWhile[1:], "goto"] #For our final stmt in the block. This will return us back to the while if
    addrIndex += 1

    threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile] = ['if'
                                                                                        ,threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile][1]
                                                                                        ,threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile][2]
                                                                                        ,threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile][3]
                                                                                        ,threeAddressCode[functionScope][blockAddressForWhile][addrIndexForWhile][4][0:7] 
                                                                                        + ', else goto L' + str(int(blockIndicator[1:]) + 1)] # We are overwriting the previous while statement. This is so the goto will be correct no matter what is within the stmts of the while loop

    blockIndicator = blockIndicator[:1] + str(int(blockIndicator[1:]) + 1)
    threeAddressCode[functionScope][blockIndicator] = {}

        
#Creates 3 address code for return statements
def _create3AddressCodeForReturnStmt(returnStmtNode):
    global threeAddressCode
    global functionScope
    global blockIndicator
    global addrIndex

    temporaryDict = {}
    returnStmtChildren = returnStmtNode.return_children()

    child = returnStmtChildren[0]

    if child.return_children() != []: #Is the return value a expression?
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

#Creates 3 address code for function calls
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
    
    elif child.return_value() == '*' or child.return_value() == '&':#Looking for pointers or memory addresses
        secondchild = child.return_children()[0]
        declValue = child.return_value() + secondchild.return_value()
        temporaryDict[addrIndex] = [declID, declValue, 'assign']
        addrIndex += 1
    else:
        exprDict = {}
        exprDict, temporaryvariableName = _create3AddressCodeForExpr(child, exprDict)
        declValue = temporaryvariableName
        temporaryDict.update(exprDict)
        temporaryDict[addrIndex-1] = [declID, temporaryDict[addrIndex-1][1], temporaryDict[addrIndex-1][2], temporaryDict[addrIndex-1][3],  'assign'] #Want to assign the variable to the previous 3addresscode variable values. Remove the assigned the tempvariable to the permanent variable
        
   
    threeAddressCode[functionScope][blockIndicator].update(temporaryDict)
    