'''
-@author: Tyler Ray
-@date: 8/23/2023

- This file is the main file of the compiler
- This program will take in a c file and output the compiled version of it
- ***WORK IN PROGRESS***

'''
import Tokenizer as tk
import argparse
import sys
import os
import re


def command_line_parser():

    parser = argparse.ArgumentParser(description='a custom python compiler for c files')

    parser.add_argument('file', help='a valid c input file', metavar='File')

    parser.add_argument('-t', action="store_true", help='outputs a tokenized version of the input file')

    args = parser.parse_args()

    return args


def validity_check(possible_input_file):
    
    if not os.path.isfile(possible_input_file): # check if file exists
        print("Please input a valid c file to compile")
        sys.exit()

    if possible_input_file[-2:] != ".c": # check if file is a c file
        print("Please input a valid c file to compile")
        sys.exit()

    return

# main function
def main():
    
    args = command_line_parser()

    possible_input_file = args.file

    validity_check(possible_input_file)

    input_file = open(possible_input_file, "r") # open file

    tk.main(input_file)

    if args.t: # if -t flag is used print out our tokens
        print(input_file) #placeholder



main()
