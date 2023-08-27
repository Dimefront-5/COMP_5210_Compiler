'''
-@author: Tyler Ray
-@date: 8/26/2023

- This file is the main file of the compiler
- This program will take in a c file and output the compiled version of it
- ***WORK IN PROGRESS***

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
    output3 = ""
    lineno = 0
    for i in tokens:
        output += "Token Number: " + str(i)
        output += " - Token Type: " + tokens[i][0]
        output += " - Token: " + str(tokens[i][1])
        output += " - Line Number: " + str(tokens[i][2])
        output += " - Column Number: " + str(tokens[i][3])
        output += "\n"

        if lineno != tokens[i][2]:
            output2 += "\n"
            output3 += "\n"
            lineno = tokens[i][2]
        output2 += "\'" + tokens[i][1] + "\' "

        output3 += tokens[i][0] + " "

    output += "\n\n\n" + output2 + "\n\n\n" + output3
    return output

# main function
def main():
    
    args = command_line_parser()

    possible_input_file = args.file

    validity_check(possible_input_file)

    input_file = open(possible_input_file, "r") # open file

    tokens = tk.main(input_file)

    if args.t: # if -t flag is used print out our tokens
       print(output_formatter(tokens))



main()
