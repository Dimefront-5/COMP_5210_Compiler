'''
-@author: Tyler Ray
-@date: 10/23/2023

- Will take a 3 address code representation and remove blocks that are blank and update gotos.
'''


def blockRemoval(threeAddrCode):
    #threeAddrCode = _blockRemovalMainLoop(threeAddrCode)
    return threeAddrCode

#------ Inward Facing modules

def _blockRemovalMainLoop(threeAddrCode):
    for scope in threeAddrCode:
        if isinstance(threeAddrCode[scope], dict): #Want to make sure we ignore global variables
            for block in list(threeAddrCode[scope]):
                isBlockBlank = _isBlockBlank(block, threeAddrCode, scope)
                if isBlockBlank == True:
                    threeAddrCode = _removeBlock(block, threeAddrCode, scope)
                
    return threeAddrCode


def _removeBlock(block, threeAddrCode, scope):
    blockNumber = block[1:]
    for otherBlocks in list(threeAddrCode[scope]):
        if otherBlocks != block:
            if blockNumber > otherBlocks[1:]:
                previousBlock = str('L' + str((int(otherBlocks[1:]) - 1)))
                threeAddrCode[scope][previousBlock] = threeAddrCode[scope][otherBlocks]

    return threeAddrCode

def _isBlockBlank(block, threaaddrCode, scope):
    if threaaddrCode[scope][block] == {}:
        return True
    return False
