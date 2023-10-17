'''
-@author: Tyler Ray
-@date: 10/12/2023

- Will take a 3 address code representation and perform constant folding on it
'''

import re

import compilerconstants as cc

#main function
def folder(threeaddrCode, changed):
    threeaddrCode, potentialChange = _constantFoldingMainLoop(threeaddrCode)

    if changed == False: #makes sure we don't remove the changed flag if it is already true
        changed = potentialChange

    return threeaddrCode, changed

#------ Inward Facing modules

#Iterates through each block in our 3 address code and calls the constant folding function on it
def _constantFoldingMainLoop(threeAddrCode):
    changed = False
    for scope in threeAddrCode:
        if isinstance(threeAddrCode[scope], dict): #Want to make sure we ignore global variables
            for block in threeAddrCode[scope]:
                threeAddrCode[scope][block], changed = _constantFoldingBlock(threeAddrCode[scope][block], changed)

    return threeAddrCode, changed

#Looks for blocks that we can perform constant folding on
def _constantFoldingBlock(block, changed):
    newBlock = {}
    for index, stmt in block.items():
        if (stmt[-1] == 'decl' or stmt[-1] == 'assign') and len(stmt) == 5: #Only stmts with 5 length can be constant folded
            stmt, potentialChange = _checkingForConstants(stmt)
            newBlock[index] = stmt
            if changed == False:#We don't want to overwrite changed if it is already true
                changed = potentialChange

    return block, changed

#Checks to see if the blocks contain constants and if so, performs the constant folding
def _checkingForConstants(stmt):
    if re.match(cc.numbers, stmt[1]) and re.match(cc.numbers, stmt[3]):
        evaluatedNumber = _foldTheConstants(stmt[1], stmt[2], stmt[3])
        if evaluatedNumber != False:
            stmt[1] = evaluatedNumber
            stmt.pop(2)
            stmt.pop(2) #We pop twice because we want to get rid of the operator and the second constant, we do the same index twice because the list shifts
            return stmt, True
        else:
            return stmt, False
    else:
        return stmt, False

#Performs the constant folding
def _foldTheConstants(constant1, operation, constant2):
    if operation != '==':
        evalString = constant1 + operation + constant2
        evaluatedNumber = eval(evalString)
        return str(evaluatedNumber)
    else:
        return False
