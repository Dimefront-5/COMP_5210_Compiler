'''
-@author: Tyler Ray
-@date: 10/31/2023

- Will take a 3 address code representation and perform copy propagation on it
'''


def copyPropagator(threeAddrCode, changed):
    threeAddrCode, potentialChange = _copyPropagatorMainLoop(threeAddrCode)

    if changed == False:
        changed = potentialChange
    
    return threeAddrCode, changed



#------ Inward Facing modules


#Iterates through each block in our 3 address code and calls the copy propagation function on it

def _copyPropagatorMainLoop(threeAddrCode):
    changed = False
    for scope in threeAddrCode:
        variables = {}#We create a dictionary that holds every variable we find in the code and what is assigned to
        if isinstance(threeAddrCode[scope], dict): #Want to make sure we ignore global variables
            for block in threeAddrCode[scope]:
                variables, potentialChange = _copyPropagatorBlock(threeAddrCode[scope][block], changed, variables)

                if changed == False:
                    changed = potentialChange

    return threeAddrCode, changed



#Iterates through the block and performs copy propagation on it
def _copyPropagatorBlock(block, changed, variables):
    for key, line in block.items():
        if line[-1] == 'decl':
            line, potentialChange = _isThisBeingAssignedToAnotherVariable(line, variables)

            block[key] = line

            if changed == False:
                changed = potentialChange
        
        elif line[-1] == 'assign':
            if line[2] == 'assign':
                line, potentialChange = _isThisBeingAssignedToAnotherVariable(line, variables)

                block[key] = line

                if changed == False:
                    changed = potentialChange

            else:#If it is a expression, we will at this to a list of variables. 
                variables[line[0]] = [line[1], line[2], line[3]]
  
    return variables, changed


#Is the variable it is assigned to being assigned to another variable?
def _isThisBeingAssignedToAnotherVariable(line, variables):
    changed = False

    if line[1] in variables:#if the varibale it is being assigned to is in our dictionary, we want to change it to what it is assigned to
        line = [line[0], variables[line[1]][0], variables[line[1]][1], variables[line[1]][2], line[-1]]
        variables[line[0]] = [line[1], line[2], line[3]]
        changed = True
    else:
        changed = False

    return line, changed
        
    