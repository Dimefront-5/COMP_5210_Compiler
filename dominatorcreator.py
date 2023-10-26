'''
-@author: Tyler Ray
-@date: 10/25/2023

- This file will take a block flow graph and create a dominator tree of the graph
'''



import networkx as nx
import matplotlib.pyplot as plt


def dominationCreation(flowGraph):
    dominatorGraphs = _dominationCreationMainLoop(flowGraph)
    return dominatorGraphs



# ------ Inward Facing Modules

def _dominationCreationMainLoop(flowGraph):
    allGraphs = {}

    for graph in flowGraph:
        edges = []
        dominatorGraph = _dominationCreationInit()
        for node in flowGraph[graph].nodes:
            for edge in flowGraph[graph].edges(node):
                edges.append(list(edge))

        dominatorGraph.add_node('L0')
        
        for edge in edges:
            if edge[0] == 'L0' and edge[1] == 'L1':
                dominatorGraph.add_edge('L0', 'L1')

            toNodeCandidate = edge[1]
            FoundOtherEdge = False
            if edge[0][1:] > toNodeCandidate[1:]:
                FoundOtherEdge = True

            for otherEdgesInNodes in edges:
                if otherEdgesInNodes[1] == toNodeCandidate and otherEdgesInNodes[0] != edge[0] and otherEdgesInNodes[0][1:] < toNodeCandidate[1:]:
                    FoundOtherEdge = True

            if FoundOtherEdge == False and edge[0][1:] < toNodeCandidate[1:]:
                dominatorGraph.add_edge(edge[0], toNodeCandidate)
            
            elif FoundOtherEdge == True and edge[0][1:] < toNodeCandidate[1:]:
                in_edges = dominatorGraph.in_edges(edge[0])
                for parentDominator in in_edges:
                    if parentDominator[0] != 'L0':
                        dominatorGraph.add_edge(parentDominator[0], toNodeCandidate)


        for node in flowGraph[graph].nodes:
            if node not in dominatorGraph.nodes:
                dominatorGraph.add_edge('L0', node)
        
        allGraphs[graph] = dominatorGraph

    return allGraphs
    




def _dominationCreationInit():
    dominatorGraph = nx.DiGraph()
    return dominatorGraph