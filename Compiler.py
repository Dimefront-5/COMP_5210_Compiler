'''
-@author: Tyler Ray
-@date: 9/24/2023

- This file is the main file of the compiler
- This program will take in a c file and output the compiled version of it
- ***WORK IN PROGRESS***
- Finished: Tokenizer, Parser
'''

import Tokenizer as tk
import Parser as ps
import ASTto3addrcode as a3
import CompilerConstants as cc

import argparse
import sys
import os


# main function
def main():
    
    args = _commandLineParser()

    possibleInputFile = args.file

    _fileValidityCheck(possibleInputFile)

    inputFile = open(possibleInputFile, "r")

    tokens = tk.main(inputFile)

    output_for_tokens, error_output = _tokenOutputFormatter(tokens) #We want to print out the tokens before we remove comments

    tokens = _removingCommentsFromDictionary(tokens) #We want to remove comments before we start to parse, that way it won't mess with our language

    parsetree, symbolTable = ps.parser(tokens)

    threeAddressCode = a3.converter(parsetree, symbolTable)

    if error_output != "":
        print("Errors found in ", possibleInputFile, ":\n\n")
        print(error_output)
        sys.exit()

    _printingOutput(args, output_for_tokens, parsetree, symbolTable, threeAddressCode, possibleInputFile)

#------ Inward Facing modules

#Has a built in help command. 
def _commandLineParser():

    parser = argparse.ArgumentParser(description='a custom python compiler for c files')

    parser.add_argument('file', help='a valid c input file', metavar='File')

    parser.add_argument('-t', action="store_true", help='outputs a tokenized version of the input file')

    parser.add_argument('-p', action="store_true", help='outputs a parse tree of the input file')

    parser.add_argument('-s', action="store_true", help='outputs a symbol table of the input file')

    parser.add_argument('-a', action="store_true", help='outputs the three address code of the input file')

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

        '''
        A pretty way to print out the tokens that represent the input file. Makes it easier to debug
        if lineno != tokens[i][2]:
            output2 += "\n"
            lineno = tokens[i][2]

        output2 += "\'" + tokens[i][1] + "\' "

    output += "\n\n\n" + output2 + "\n\n\n"
        '''

    return output, errorOutput

#Removes comments that are found within our dictionary, and returns a new dictionary without the comments that is ordered correctly
def _removingCommentsFromDictionary(dictionary):
    newIndex = 0
    newDictionary = {}
    for key in dictionary.keys():
        if dictionary[key][cc.TOKEN_TYPE_INDEX] != "comment" and dictionary[key][cc.TOKEN_TYPE_INDEX] != 'commentStart' and dictionary[key][cc.TOKEN_TYPE_INDEX] != 'commentEnd':
            newDictionary[str(newIndex)] = dictionary[key]
            newIndex += 1

    return newDictionary


def _printingOutput(args, output_for_tokens, parsetree, symbolTable, threeAddressCode, possibleInputFile):
    if args.t:
        print(output_for_tokens)

    if args.p:
        if parsetree == None:
           print("Errors found in ", possibleInputFile, ":")
           print("\tSyntax Error\n\n")
           sys.exit()
        else:
            print(parsetree)

    if args.s:
        if symbolTable == None:
            print("Errors found in ", possibleInputFile, ":")
            print("\tSyntax Error\n\n")
            sys.exit()
        else:
            print(symbolTable)

    if args.a:
        if threeAddressCode == None:
            print("Errors found in ", possibleInputFile, ":")
            print("\tSyntax Error\n\n")
            sys.exit()
        else:
            print(threeAddressCode)

if __name__ == "__main__":
    main()
