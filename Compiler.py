'''
-@author: Tyler Ray
-@date: 8/31/2023

- This file is the main file of the compiler
- This program will take in a c file and output the compiled version of it
- ***WORK IN PROGRESS***
- Finished with the tokenizer and our simple command line parser

'''

import Tokenizer as tk
import argparse
import sys
import os


#Built in help command. Only flag we need it -t
def command_line_parser():

    parser = argparse.ArgumentParser(description='a custom python compiler for c files')

    parser.add_argument('file', help='a valid c input file', metavar='File')

    parser.add_argument('-t', action="store_true", help='outputs a tokenized version of the input file')

    args = parser.parse_args()

    return args


def validity_check(possible_input_file):
    
    if not os.path.isfile(possible_input_file): # check if file exists
        print("Please check to see if the file exists and is stored in the same directory as the compiler")
        sys.exit()

    if possible_input_file[-2:] != ".c": # check if file is a c file
        print("Please input a valid c file to compile")
        sys.exit()

    return

#Might be a better way to format this, but this works for now
def output_formatter(tokens):

    #Better formatting
    output = ""
    output2 = ""
    error_output = ""
    lineno = 0
    for i in tokens:
        if "ERROR" in tokens[i][0]:
            error_output += tokens[i][0] + ":\n\tline number,column number - " + str(tokens[i][2]) + "," + str(tokens[i][3]) + "\t\'" + tokens[i][1] + "\'" +  "\n"
            continue

        output += "Token Type: " + tokens[i][0]
        output += " - Token: " + str(tokens[i][1])
        output += " - Line Number, Column Number: " + str(tokens[i][2]) + "," + str(tokens[i][3])
        output += "\n"

        '''
        A pretty way to print out the tokens that represent the input file. Makes it easier to debug
        if lineno != tokens[i][2]:
            output2 += "\n"
            lineno = tokens[i][2]

        output2 += "\'" + tokens[i][1] + "\' "

    output += "\n\n\n" + output2 + "\n\n\n"
        '''

    return output, error_output


# main function
def main():
    
    args = command_line_parser()

    possible_input_file = args.file

    validity_check(possible_input_file)

    input_file = open(possible_input_file, "r") # open file

    tokens = tk.main(input_file)

    output_for_tokens, error_output = output_formatter(tokens)

    if error_output != "":
        print("Errors found in ", possible_input_file, ":\n\n")
        print(error_output)
        sys.exit()

    if args.t: # if -t flag is used print out our tokens
       print(output_for_tokens)

main()
