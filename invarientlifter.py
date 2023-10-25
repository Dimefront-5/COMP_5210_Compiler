'''
-@author: Tyler Ray
-@date: 10/24/2023

- Will take a 3 address code representation and remove invariant loops from it
'''

def invariantLifter(threeAddrCode, changed):
    #threeAddrCode, potentialChange = _invariantLifterMainLoop(threeAddrCode)
    
    return threeAddrCode, changed


#------ Inward Facing modules

def _invariantLifterMainLoop(threeAddrCode):
    changed = False
    for scope in threeAddrCode:
        if isinstance(threeAddrCode[scope], dict):
            for block in threeAddrCode[scope]:
                threeAddrCode[scope][block], potentialChange = _invariantLifterBlock(threeAddrCode[scope][block], threeAddrCode, scope, block)
                
                if changed == False:
                    changed = potentialChange

    return threeAddrCode, changed


def _invariantLifterBlock(block, threeAddrCode, scope, blockName):
    for key, value in block.items():

        if value[0] == 'if':
            pass
    
    return threeAddrCode[scope][blockName], False