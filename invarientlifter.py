'''
-@author: Tyler Ray
-@date: 10/24/2023

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
                        threeAddrCode, potentialChange = _invariantLifterBlock(threeAddrCode[name][edge[0]], threeAddrCode, name, dominatingNodeWithinLoop, edge[1])

                        if changed == False:
                            changed = potentialChange

    return threeAddrCode, changed
            



def _invariantLifterBlock(block, threeAddrCode, scope, blockName, blockToMoveTo):
    changed = False

    loopVariants = []
    for key, line in list(threeAddrCode[scope][blockToMoveTo].items()):
        print(line)
        if line[0] == 'if':
            if re.match(cc.identifiers, line[1]):
                loopVariants.append(line[1])
            
            if re.match(cc.identifiers, line[3]):
                loopVariants.append(line[3])
    
    for key, line in list(block.items()):
        if line[-1] == 'assign':
            if line[2] == 'assign': #Meaning there is no operator
                if not line[1] in loopVariants:
                    tempDict = {}
                    tempDict[key] = line
                    for tempKey, tempLine in list(threeAddrCode[scope][blockToMoveTo].items()):
                        tempDict[tempKey] = tempLine
                        threeAddrCode[scope][blockToMoveTo].pop(tempKey)

                    threeAddrCode[scope][blockToMoveTo] = tempDict

                    threeAddrCode[scope][blockName].pop(key)
                    changed = True

    
    return threeAddrCode, changed