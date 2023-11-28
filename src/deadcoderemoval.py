'''
-@author: Tyler Ray
-@date: 10/31/2023

- Will take a 3 address code representation and remove dead code from it
'''
import compilerconstants as cc
import re

def deadCodeRemover(threeAddrCode, changed):
    newThreeAddrCode, potentialChange = _iteratingThroughCode(threeAddrCode)

    if changed == False:
        changed = potentialChange

    return newThreeAddrCode, changed


#------ Inward Facing modules

def _iteratingThroughCode(threeAddrCode):
    changed = False
    #deadCodeCandidates looks for variables that aren't used in the code. The key is the variable name and the value is a boolean that is true if the variable is used and false if it isn't along with the block and the addrIndex
    for scope in threeAddrCode:
        deadCodeCandidates = {}
        if isinstance(threeAddrCode[scope], dict): #Ignoring global variables for now
            for block in threeAddrCode[scope]:
                deadCodeCandidates = _iteratingThroughBlock(threeAddrCode[scope][block], deadCodeCandidates, threeAddrCode, block, scope)
            
            threeAddrCode, changed = _removingDeadCode(threeAddrCode, deadCodeCandidates)
        

    #Now we need to iterate through the deadCodeCandidates and remove the ones that are false
    return threeAddrCode, changed


def _iteratingThroughBlock(block, deadCodeCandidates, threeAddrCode, blockName, scope):
    for key, line in list(block.items()):
        if line[-1] == 'assign' or line[-1] == 'decl' or line[-1] == 'return' or line[-1] == 'param':
            
            deadCodeCandidates = _areVariablesUsedInThisBlock(line, deadCodeCandidates)

            if line[1] == '' and line[-1] == 'decl':
                threeAddrCode[scope][blockName].pop(key)

            if line[0] not in deadCodeCandidates and line[0].isnumeric() == False and line[1] != '' and line[-1] != 'return':
                deadCodeCandidates[line[0]] = [False, scope, blockName, key]

        elif line[0] == 'if':
            deadCodeCandidates = _areVariablesUsedInThisBlock(line, deadCodeCandidates)

    return deadCodeCandidates

#Checks to see if the variables are used in the line, if they are, it will set the boolean to true
def _areVariablesUsedInThisBlock(line, deadCodeCandidates):
    if line[-1] == 'param':
        deadCodeCandidates[line[0]] = [True, '', '', '']

    elif line[-1] == 'return':
        if line[0] in deadCodeCandidates:
            deadCodeCandidates[line[0]][0] = True

    elif line[-1] == 'assign' and line[2] == 'assign': #Doesn't have a operator meaning it is a single assignment
        if line[1] in deadCodeCandidates:
            deadCodeCandidates[line[1]][0] = True

    elif line[-1] == 'decl':
        if line[1] in deadCodeCandidates:
            deadCodeCandidates[line[1]][0] = True
    else:
        if line[1] in deadCodeCandidates:
            deadCodeCandidates[line[1]][0] = True
        elif re.match(cc.identifiers, line[1]): #We want to add the variable to the deadCodeCandidates if it isn't in there if it used in a if statement
            deadCodeCandidates[line[1]] = [True, '', '', '']
            
        if line[3] in deadCodeCandidates:
            deadCodeCandidates[line[3]][0] = True

        elif re.match(cc.identifiers, line[3]): #We want to add the variable to the deadCodeCandidates if it isn't in there if it used in a if statement
            deadCodeCandidates[line[3]] = [True, '', '', '']
    
    return deadCodeCandidates

#Removes every line that is dead code
def _removingDeadCode(threeAddrCode, deadCodeCandidates):
    changed = False

    for key, value in deadCodeCandidates.items():
        if value[0] == False:
            changed = True
            threeAddrCode[value[1]][value[2]].pop(value[3])

    return threeAddrCode, changed