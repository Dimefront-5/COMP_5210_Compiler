'''
-@author: Tyler Ray
-@date: 10/26/2023

- Will take a 3 address code representation and remove invariants from loops
'''
import compilerconstants as cc
import re
import networkx as nx



def invariantLifter(threeAddrCode, changed, controlFlowGraph, dominatorGraph):
    threeAddrCode, potentialChange = _invariantLifterMainLoop(threeAddrCode, controlFlowGraph, dominatorGraph)

    if changed == False:
        changed = potentialChange
    
    return threeAddrCode, changed


#------ Inward Facing modules

#Finds all invarients in the code and lifts them out of the loop and then will report back any changes
def _invariantLifterMainLoop(threeAddrCode, controlFlowGraph, dominatorGraph):
    changed = False

    for name, graph in controlFlowGraph.items(): #look through each function
        domGraph = dominatorGraph[name]

        for node in graph.nodes:
            inwardNodes = graph.in_edges(node)#We only want to look at the inward edges

            for edge in inwardNodes:
                if edge[0][1:] > edge[1][1:]:#Is the edge pointing to a previous node in the graph?
                    doesItDominate = nx.has_path(domGraph, edge[1], edge[0]) #Is the previous node dominating the node?

                    if doesItDominate == True:

                        dominatingNodeWithinLoop = 'L' + str(int(edge[1][1:]) + 1) #Within my loop, the dominating node that contains the while code will be the block after the if statement block.
                        potentialInvarients = _potentialInvarientFinder(threeAddrCode[name][dominatingNodeWithinLoop], threeAddrCode, name, dominatingNodeWithinLoop, edge[1])

                        finalBlockInLoop = _finalBlockFinder(controlFlowGraph[name], edge[1])

                        potentialInvarients = _invarientFinder(threeAddrCode, potentialInvarients, name, finalBlockInLoop, dominatingNodeWithinLoop)

                        threeAddrCode, potentialChange = _invarientLifter(threeAddrCode, potentialInvarients, name, edge[1])

                        if changed == False:
                            changed = potentialChange

    return threeAddrCode, changed
            


#Looks through dominating node and finds all potential invarients
def _potentialInvarientFinder(block, threeAddrCode, scope, blockName, blockToMoveTo):
    potentialInvariants = {}
    loopVariants = []

    for key, line in list(threeAddrCode[scope][blockToMoveTo].items()):#Adds loop variants to a list
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

#Finds the final block in the loop that calls the dominating node
def _finalBlockFinder(controlFlowGraph, ifBlock):
    allEdges = controlFlowGraph.edges
    
    for edge in allEdges:
        if edge[0][1:] > edge[1][1:] and edge[1] == ifBlock:
            return edge[0]
    
#Finds all instances of the invarients in the loop if they appear
def _invarientFinder(threeAddrCode, potentialInvariants, scope, finalBlockInLoop, dominatingNodeWithinLoop):

    currentBlock = 'L' + str(int(dominatingNodeWithinLoop[1:]) + 1) #We start on the block after the dominating node within the loop
    blockPastLoop = 'L' + str(int(finalBlockInLoop[1:]) + 1) #We want to stop at the block after the loop

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

#Lifts our invarients out of the loop
def _invarientLifter(threeAddrCode, potentialInvariants, scope, blockToMoveTo):
    changed = False
    for variable, information in reversed(potentialInvariants.items()): #Reverse it so the instructions appear in the right order when we move them

        if information[0] == False: #We are reordering the lines so they appear in the right order and have the if statement at the end.
            #If I had used a list within a list, I could add it to the front, but I am using a dictionary so I have to add it to the back.
            tempDict = {}
            tempDict[information[3]] = threeAddrCode[scope][information[2]][information[3]]

            for tempKey, tempLine in list(threeAddrCode[scope][blockToMoveTo].items()):
                tempDict[tempKey] = tempLine
                threeAddrCode[scope][blockToMoveTo].pop(tempKey)

            threeAddrCode[scope][blockToMoveTo] = tempDict

            threeAddrCode[scope][information[2]].pop(information[3])
            changed = True

    return threeAddrCode, changed
