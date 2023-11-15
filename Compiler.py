'''
-@author: Tyler Ray
-@date: 11/7/2023

- This file is the main file of the compiler
- This program will take in a c file and output the compiled version of it
- ***WORK IN PROGRESS***
- Finished: Tokenizer, Parser, 3 Address Code Generator, optimizer
'''

import tokenizer as tk
import custom_parser as ps
import astto3addrcode as a3
import compilerconstants as cc
import constantpropagation as cp
import constantfolder as cf
import deadcoderemoval as dcr
import copypropagation as cpy
import dominatorcreator as dc
import invarientlifter as il
import asmcodeshaper as acs

import argparse
import sys
import os
import networkx as nx
import matplotlib.pyplot as plt

import warnings
warnings.filterwarnings("ignore") #This is so we can ignore the matplotlib warning for using a deprecated extension


# main function
def main():
    
    args = _commandLineParser()

    possibleInputFile = args.file

    _fileValidityCheck(possibleInputFile)

    inputFile = open(possibleInputFile, "r")

    tokens = tk.main(inputFile)

    output_for_tokens, error_output = _tokenOutputFormatter(tokens) #We want to print out the tokens before we remove comments

    if error_output != "":
        print("Errors found in ", possibleInputFile, ":\n\n")
        print(error_output)
        sys.exit()

    tokens = _removingCommentsFromDictionary(tokens) #We want to remove comments before we start to parse, that way it won't mess with our language

    parsetree, symbolTable = ps.parser(tokens)

    threeAddressCode, flowGraph = a3.converter(parsetree, symbolTable)

    if args.a: #This is so we can print out the unoptimized code
        output = _creatingOutputFor3AddressCode(threeAddressCode)
        print("Unoptimized Three Address Code: ")
        print(output)

    dominatorGraph = dc.dominationCreation(flowGraph)

    optimizedThreeAddressCode = optimizerLoop(threeAddressCode, flowGraph, dominatorGraph) #This is where we will call the optimizer, for the ungraded checkpoint ignore this

    assemblyCode = acs.codeShaper(optimizedThreeAddressCode, symbolTable)

    with open('output.asm', 'w') as f:
        f.write(assemblyCode.__str__())

    _printingOutput(args, output_for_tokens, parsetree, symbolTable, optimizedThreeAddressCode, flowGraph, dominatorGraph, assemblyCode)

#------ Inward Facing modules

def optimizerLoop(threeAddressCode, flowGraph, dominatorGraph):
    threeAddressCode, changed = cp.propagator(threeAddressCode)
    threeAddressCode, changed = cf.folder(threeAddressCode, changed)
    threeAddressCode, changed = dcr.deadCodeRemover(threeAddressCode, changed)
    threeAddressCode, changed = cpy.copyPropagator(threeAddressCode, changed)
    threeAddressCode, changed = il.invariantLifter(threeAddressCode, changed, flowGraph, dominatorGraph)


    while changed == True:
        threeAddressCode, changed = cp.propagator(threeAddressCode)
        threeAddressCode, changed = cf.folder(threeAddressCode, changed)
        threeAddressCode, changed = dcr.deadCodeRemover(threeAddressCode, changed)
        threeAddressCode, changed = cpy.copyPropagator(threeAddressCode, changed)
        threeAddressCode, changed = il.invariantLifter(threeAddressCode, changed, flowGraph, dominatorGraph)

    return threeAddressCode


#Has a built in help command. 
def _commandLineParser():

    parser = argparse.ArgumentParser(description='a custom python compiler for c files')

    parser.add_argument('file', help='a valid c input file', metavar='File')

    parser.add_argument('-t', action="store_true", help='outputs a tokenized version of the input file')

    parser.add_argument('-p', action="store_true", help='outputs a abstract syntax tree of the input file')

    parser.add_argument('-s', action="store_true", help='outputs a symbol table of the input file')

    parser.add_argument('-a', action="store_true", help='outputs the three address code of the input file')

    parser.add_argument('-o', action="store_true", help='outputs the optimized three address code of the input file')

    parser.add_argument('-g', action="store_true", help='outputs the flow graph of the input file')

    parser.add_argument('-d', action="store_true", help='outputs the dominator graph of the input file')

    parser.add_argument('-asm', action="store_true", help='outputs the assembly code of the input file')

    args = parser.parse_args()

    return args


def _fileValidityCheck(possible_input_file):
    
    if not os.path.isfile(possible_input_file):
        print("Please check to see if the file exists, this is an invalid file path")
        sys.exit()

    if possible_input_file[-2:] != ".c": 
        print("Please input a valid c file to compile")
        sys.exit()

def _tokenOutputFormatter(tokens):

    output = ""
    errorOutput = ""
    for i in tokens:
        if "ERROR" in tokens[i][cc.TOKEN_TYPE_INDEX]:
            errorOutput += tokens[i][cc.TOKEN_TYPE_INDEX] + ":\n\tline number,column number - " + str(tokens[i][cc.LINE_NUMBER_INDEX]) + ","\
                        + str(tokens[i][cc.COLUMN_NUMBER_INDEX]) + "\t\'" + tokens[i][cc.TOKEN_INDEX] + "\'" +  "\n"
            continue
        
        output += "Token Type: " + tokens[i][cc.TOKEN_TYPE_INDEX]
        output += " - Token: " + str(tokens[i][cc.TOKEN_INDEX])
        output += " - Line Number, Column Number: " + str(tokens[i][cc.LINE_NUMBER_INDEX]) + "," + str(tokens[i][cc.COLUMN_NUMBER_INDEX])
        output += "\n"


    return output, errorOutput

def _creatingOutputFor3AddressCode(threeAddressCode):
    indent = 0
    output = ''
    for children in threeAddressCode:
        indent = 5
        if isinstance(threeAddressCode[children], dict):
            output += ' ' * indent + children + ':\n'
            for blockIndicator in threeAddressCode[children]:
                indent = 8
                output += ' ' * indent + blockIndicator + ':\n'
                indent = 11
                for child, value in threeAddressCode[children][blockIndicator].items():
                    if value[-1] == 'return':
                        output += ' ' * indent + 'return ' + value[0] + '\n'
                            
                    elif value[-1] == 'expr':
                        output += ' ' * indent + value[0] + '\n'

                    elif value[-1] == 'goto':
                        output += ' ' * indent + 'goto ' +  value[0] + '\n'

                    elif value[0] == 'if':
                        output += ' ' * indent + 'if (' + value[1]  + ' ' + value[2] + ' ' + value[3] + ') ' + value[4] + value[5] + value[6] + value[7] +'\n'

                    elif len(value) == 4 and value[3] == 'decl':
                        if value[1] != '':
                            output += ' ' * indent + value[0] + ' = ' + value[1] + '\n'

                    elif len(value) == 5 and value[-1] == 'decl':
                        output += ' ' * indent + value[0] + ' = ' + value[1] + ' ' + value[2] + ' ' + value[3] + '\n'
                    elif value[2] == 'functionCall':
                        args = ''
                        for arg in value[1]:
                            args += arg + ', '
                        args = args[:-2]

                        output += ' ' * indent + 'call ' +  value[0] + '(' + args + ')\n'

                    elif value[-1] == 'assign':
                        if len(value) < 5:
                            output += ' ' * indent + value[0] + ' = ' + value[1] + '\n'
                        elif value[2] == '()':
                            output += ' ' * indent + value[0] + ' = (' + value[1] + ')\n' 
                        else:
                            output += ' ' * indent + value[0] + ' = ' + value[1] + ' ' + value[2] + ' ' + value[3] + '\n'
        else:
            output += 'global:\n' + ' ' * 3 + children + ' = ' + threeAddressCode[children] + '\n' 

    return output

#Removes comments that are found within our dictionary, and returns a new dictionary without the comments that is ordered correctly
def _removingCommentsFromDictionary(dictionary):
    newIndex = 0
    newDictionary = {}
    for key in dictionary.keys():
        if dictionary[key][cc.TOKEN_TYPE_INDEX] != "comment" and dictionary[key][cc.TOKEN_TYPE_INDEX] != 'commentStart' and dictionary[key][cc.TOKEN_TYPE_INDEX] != 'commentEnd':
            newDictionary[str(newIndex)] = dictionary[key]
            newIndex += 1

    return newDictionary


def _printingOutput(args, output_for_tokens, parsetree, symbolTable, optimizedCode, flowGraph, dominatorGraphs, assemblyCode = None):
    if args.t:
        print(output_for_tokens)

    if args.p:
        print(parsetree)

    if args.s:    
        print(symbolTable)

    if args.o:
        print("Optimized Code: ")
        output = _creatingOutputFor3AddressCode(optimizedCode)
        print(output)

    if args.g:
        overallFlowGraph = nx.DiGraph()
        for key, value in flowGraph.items():
            if len(value.nodes) == 1:
                nodes = value.nodes
                for node in nodes:
                    overallFlowGraph.add_node(node)

            for edge in value.edges:
                overallFlowGraph.add_edge(edge[0],edge[1])

        if len(overallFlowGraph.nodes) == 0:
            print("No flow graph to print out")
        else:
            pos = nx.nx_pydot.graphviz_layout(overallFlowGraph, prog="dot")#I reused this from Oxide
            plt.title('flow graph')
            nx.draw(overallFlowGraph, pos=pos, with_labels=True, node_size=1200, arrows=True)
            plt.show()
            

    if args.d:
        overallDominatorGraph = nx.DiGraph()
        for key, value in dominatorGraphs.items():
            for edge in value.edges:
                overallDominatorGraph.add_edge(edge[0],edge[1])
        
        if len(overallDominatorGraph.nodes) == 0:
            print("No dominator graph to print out")
        else:
            pos = nx.nx_pydot.graphviz_layout(overallDominatorGraph, prog="dot") #I reused this from Oxide
            plt.title('dominator graph')
            nx.draw(overallDominatorGraph, pos=pos, with_labels=True, node_size=1200, arrows=True)
            plt.show()

    if args.asm:
        print("Assembly Code: ")
        print(assemblyCode)


if __name__ == "__main__":
    main()
