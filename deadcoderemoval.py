'''
-@author: Tyler Ray
-@date: 10/17/2023

- Will take a 3 address code representation and remove dead code from it
'''

def deadCodeRemover(threeAddrCode, changed):
    print(threeAddrCode)
    newThreeAddrCode, potentialChange = _iteratingThroughCode(threeAddrCode)

    if changed == False:
        changed = potentialChange

    return newThreeAddrCode, changed


#------ Inward Facing modules

def _iteratingThroughCode(threeAddrCode):
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
        if line[-1] == 'assign' or line[-1] == 'decl' or line[-1] == 'return':
            
            deadCodeCandidates = _areVariablesUsedInThisBlock(line, deadCodeCandidates)

            if line[1] == '' and line[-1] == 'decl':
                threeAddrCode[scope][blockName].pop(key)
            if line[0] not in deadCodeCandidates and line[0].isnumeric() == False and line[1] != '':
                deadCodeCandidates[line[0]] = [False, scope, blockName, key]

        elif line[0] == 'if':
            deadCodeCandidates = _areVariablesUsedInThisBlock(line, deadCodeCandidates)

    return deadCodeCandidates



def _areVariablesUsedInThisBlock(line, deadCodeCandidates):
    if line[1] == 'return':
        if line[0] in deadCodeCandidates:
            deadCodeCandidates[line[0]][0] = True

    elif line[2] == 'assign': #Doesn't have a operator meaning it is a single assignment
        if line[1] in deadCodeCandidates:
            deadCodeCandidates[line[1]][0] = True
        elif line[0] in deadCodeCandidates:
            deadCodeCandidates[line[0]][0] = True

    elif line[3] == 'decl':
        if line[1] in deadCodeCandidates:
            deadCodeCandidates[line[1]][0] = True
    else:
        if line[1] in deadCodeCandidates:
            deadCodeCandidates[line[1]][0] = True
        if line[3] in deadCodeCandidates:
            deadCodeCandidates[line[3]][0] = True
    
    return deadCodeCandidates


def _removingDeadCode(threeAddrCode, deadCodeCandidates):

    changed = False
    for key, value in deadCodeCandidates.items():
        if value[0] == False:
            changed = True
            threeAddrCode[value[1]][value[2]].pop(value[3])

    return threeAddrCode, changed