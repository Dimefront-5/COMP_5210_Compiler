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
        dominatorGraph = _dominationCreationInit(flowGraph[graph])
        for node in flowGraph[graph].nodes:
            for edge in flowGraph[graph].edges(node):
                edges.append(list(edge))

        dominatorGraph.add_node('L0')
        
        for edge in edges:
            if edge[0] == 'L0' and edge[1] == 'L1':
                dominatorGraph.add_edge('L0', 'L1')

            toNodeCandidate = edge[1]
            FoundOtherEdge = False
            for otherEdgesInNodes in edges:
                if otherEdgesInNodes[1] == toNodeCandidate and otherEdgesInNodes[0] != edge[0] and edge[0][1:] > toNodeCandidate[1:]:
                    FoundOtherEdge = True

            if FoundOtherEdge == False and edge[0][1:] < toNodeCandidate[1:]:
                dominatorGraph.add_edge(edge[0], toNodeCandidate)
        
        allGraphs[graph] = dominatorGraph

    return allGraphs
    




def _dominationCreationInit(flowGraph):
    dominatorGraph = nx.DiGraph()
    return dominatorGraph