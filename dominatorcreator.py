'''
-@author: Tyler Ray
-@date: 10/31/2023

- This file will take a block flow graph and create a dominator tree of the graph
'''

import networkx as nx


def dominationCreation(flowGraph):
    dominatorGraphs = _dominationCreationMainLoop(flowGraph)
    return dominatorGraphs



# ------ Inward Facing Modules

#Walks through each controlFlowGrpah and creates a dominator graph for each one
def _dominationCreationMainLoop(flowGraph):
    allGraphs = {}

    for graph in flowGraph:
        edges = []
        for node in flowGraph[graph].nodes:
            for edge in flowGraph[graph].edges(node):
                edges.append(list(edge)) #Gets every edge in the graph

        dominatorGraph = _creatingDominatorGraphFromEdges(flowGraph, graph, edges)
        
        allGraphs[graph] = dominatorGraph

    return allGraphs

#Will take the edges and our flowGraph and create a dominator graph from it
def _creatingDominatorGraphFromEdges(flowGraph, graph, edges):
    dominatorGraph = _dominationCreationInit()
    dominatorGraph.add_node('L0')
    if len(edges) == 0:
        return dominatorGraph
    firstnode = edges[0][0]
    for edge in edges:
        if edge[0] == firstnode:
            dominatorGraph.add_edge(firstnode, edge[1])

        toNodeCandidate = edge[1]
        FoundOtherEdge = False
        PointToEachOther = False
        if edge[0][1:] > toNodeCandidate[1:]: #If the edge is going backwards in the graph, we don't want to add it
            FoundOtherEdge = True

        for otherEdgesInNodes in edges:
            if otherEdgesInNodes[1] == toNodeCandidate and otherEdgesInNodes[0] != edge[0] and otherEdgesInNodes[0][1:] < toNodeCandidate[1:]: #If there is another edge going to the same node, we don't want to add it
                FoundOtherEdge = True
                if flowGraph[graph].has_edge(edge[0], otherEdgesInNodes[0]) == True:
                    PointToEachOther = True

        if FoundOtherEdge == False and edge[0][1:] < toNodeCandidate[1:]:#if we didn't find another edge going to the same node, we want to say it is dominating it
            dominatorGraph.add_edge(edge[0], toNodeCandidate)
        
        elif PointToEachOther == True: #If one node points to one and then the one after, we want to add the edge
            dominatorGraph.add_edge(edge[0], toNodeCandidate)

        elif FoundOtherEdge == True and edge[0][1:] < toNodeCandidate[1:]:#If there are multiple edges going to the same node, we want to find the one that is dominating it, wil be dominating the other one
            in_edges = dominatorGraph.in_edges(edge[0])
            for parentDominator in in_edges:
                if parentDominator[0] != firstnode:#ignore the first node
                    dominatorGraph.add_edge(parentDominator[0], toNodeCandidate)

    for node in flowGraph[graph].nodes:#This will add any nodes that aren't in the dominator graph
        if node not in dominatorGraph.nodes:
            dominatorGraph.add_edge(firstnode, node)

    return dominatorGraph

def _dominationCreationInit():
    dominatorGraph = nx.DiGraph()
    return dominatorGraph