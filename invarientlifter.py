'''
-@author: Tyler Ray
-@date: 10/26/2023

- Will take a 3 address code representation and remove invariant loops from it
'''
import compilerconstants as cc
import re



def invariantLifter(threeAddrCode, changed, controlFlowGraph, dominatorGraph):
    threeAddrCode, potentialChange = _invariantLifterMainLoop(threeAddrCode, controlFlowGraph, dominatorGraph)

    if changed == False:
        changed = potentialChange
    
    return threeAddrCode, changed


#------ Inward Facing modules

def _invariantLifterMainLoop(threeAddrCode, controlFlowGraph, dominatorGraph):
    changed = False

    for name, graph in controlFlowGraph.items():
        domGraph = dominatorGraph[name]

        for node in graph.nodes:
            inwardNodes = graph.in_edges(node)

            for edge in inwardNodes:
                if edge[0][1:] > edge[1][1:]:
                    doesItDominate = domGraph.has_edge(edge[1], edge[0])

                    if doesItDominate == True:
                        dominatingNodeWithinLoop = 'L' + str(int(edge[1][1:]) + 1)
                        potentialInvarients = _potentialInvarientFinder(threeAddrCode[name][edge[0]], threeAddrCode, name, dominatingNodeWithinLoop, edge[1])
                        
                        finalBlockInLoop = _finalBlockFinder(controlFlowGraph[name], edge[1])

                        potentialInvarients = _invarientFinder(threeAddrCode, potentialInvarients, name, dominatingNodeWithinLoop, finalBlockInLoop)

                        threeAddrCode, potentialChange = _invarientLifter(threeAddrCode, potentialInvarients, name, edge[1])

                        if changed == False:
                            changed = False

    return threeAddrCode, changed
            



def _potentialInvarientFinder(block, threeAddrCode, scope, blockName, blockToMoveTo):
    changed = False
    potentialInvariants = {}
    loopVariants = []
    for key, line in list(threeAddrCode[scope][blockToMoveTo].items()):
        if line[0] == 'if':
            if re.match(cc.identifiers, line[1]):
                loopVariants.append(line[1])
            
            if re.match(cc.identifiers, line[3]):
                loopVariants.append(line[3])
    
    for key, line in list(block.items()):
        if line[-1] == 'assign':
            if line[2] == 'assign':
                if line[0] and line[1] not in loopVariants:
                    potentialInvariants[line[0]] = [False, scope, blockName, key]
            elif line[1] not in loopVariants and line[3] not in loopVariants and line[0] not in loopVariants:
                potentialInvariants[line[0]] = [False, scope, blockName, key]

    return potentialInvariants

def _finalBlockFinder(controlFlowGraph, ifBlock):
    allEdges = controlFlowGraph.edges
    
    for edge in allEdges:
        if edge[0][1:] > edge[1][1:] and edge[1] == ifBlock:
            return edge[0]
    

def _invarientFinder(threeAddrCode, potentialInvariants, scope, finalBlockInLoop, dominatingNodeWithinLoop):

    currentBlock = 'L' + str(int(dominatingNodeWithinLoop[1:]) + 1)
    blockPastLoop = 'L' + str(int(finalBlockInLoop[1:]) + 1)

    while currentBlock != blockPastLoop:
        
        for line in threeAddrCode[scope][currentBlock].values():
            if line[-1] == 'assign':
                if line[0] in potentialInvariants:
                    potentialInvariants[line[0]][0] = True
                if line[2] != 'assign':
                    if line[1] in potentialInvariants:
                        potentialInvariants[line[1]][0] = True
                    if line[3] in potentialInvariants:
                        potentialInvariants[line[3]][0] = True
            elif line[-1] == 'if':
                if line[1] in potentialInvariants:
                    potentialInvariants[line[1]][0] = True
                if line[3] in potentialInvariants:
                    potentialInvariants[line[3]][0] = True
            elif line[-1] == 'return':
                if line[0] in potentialInvariants:
                    potentialInvariants[line[0]][0] = True
        
        currentBlock = 'L' + str(int(currentBlock[1:]) + 1)
                

    return potentialInvariants




def _invarientLifter(threeAddrCode, potentialInvariants, scope, blockToMoveTo):
    
    changed = False
    for variable, information in potentialInvariants.items():
        if information[0] == False:
            changed = False #Change to TRUE when we actually do the lifting
            pass #Going to have to do the reordering thing here since it's a dict. TODO

    return threeAddrCode, changed
