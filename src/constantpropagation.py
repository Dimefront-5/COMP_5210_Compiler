'''
-@author: Tyler Ray
-@date: 10/11/2023

- Will take a 3 address code representation and perform constant propagation on it
'''

import re
import copy

import compilerconstants as cc


#Calls the iteratingThroughCode function and returns the new 3 address code and whether or not it changed
def propagator(threeAddrCode):
    newThreeAddrCode, changed = _iteratingThroughCode(threeAddrCode)
    return newThreeAddrCode, changed


#------ Inward Facing modules

def _iteratingThroughCode(threeAddrCode):
    changed = False
    newthreeAddrCode = copy.deepcopy(threeAddrCode)
    for scope in newthreeAddrCode:
        if isinstance(newthreeAddrCode[scope], dict): #Ignoring global variables for now
            for block in newthreeAddrCode[scope]:
                newBlock, changed = _lookingForConstants(threeAddrCode[scope][block], changed)
                newthreeAddrCode[scope][block] = newBlock

    return newthreeAddrCode, changed

#This will iterate through the statements in a block and look for constants
def _lookingForConstants(stmtsInBlock, changed):
    variablesWithConstants = {}
    newBlock = {}

    for value, stmt in stmtsInBlock.items():
        if stmt[-1] == 'decl':
            if re.match(cc.exprOps, stmt[2]) == None: #If we don't find a relational Operator, it has the chance to be a assignment to just a constant
                stmt, changed = _checkingForConstant(variablesWithConstants, stmt, changed)
                newBlock[value] = stmt
            else:
                for i in stmt: #If we do, iterate through the statement and see if we can replace any variables with constants, but ignore what we are assigning to
                    if i in variablesWithConstants and i != stmt[0]:
                        constant = variablesWithConstants[i]
                        stmt[stmt.index(i)] = constant
                        changed = True

                newBlock[value] = stmt

        elif stmt[-1] == 'assign':                
            if re.match(cc.exprOps, stmt[2]) == None: #If we don't find a relational Operator, it has the chance to be a assignment to just a constant
                stmt, changed = _checkingForConstant(variablesWithConstants, stmt, changed)
                newBlock[value] = stmt
            else:
                for i in stmt: #If we do, iterate through the statement and see if we can replace any variables with constants, but ignore what we are assigning to
                    if i in variablesWithConstants and i != stmt[0]:
                        constant = variablesWithConstants[i]
                        stmt[stmt.index(i)] = constant
                        changed = True
                
                if stmt[0] in variablesWithConstants:
                    del variablesWithConstants[stmt[0]]

                newBlock[value] = stmt

        elif stmt[-1] == 'return':
            if stmt[0] in variablesWithConstants:
                stmt[0] = variablesWithConstants[stmt[0]]
                changed = True

            newBlock[value] = stmt
        else:
            newBlock[value] = stmt

    return newBlock, changed

#Will check to see if the stmt value at 1 is a constant number or is a variable that has a constant value. If it is, it will replace it with the constant value
def _checkingForConstant(variablesWithConstants, stmt, changed):

    if re.match(cc.numbers, stmt[1]): #If the value is a negative number, we want to make sure we don't treat the negative sign as a variable
        variablesWithConstants[stmt[0]] = stmt[1]

    elif stmt[1] in variablesWithConstants:
        stmt[1] = variablesWithConstants[stmt[1]]
        changed = True

    elif stmt[0] in variablesWithConstants:
        del variablesWithConstants[stmt[0]]

    return stmt, changed


        

        
        

        




    