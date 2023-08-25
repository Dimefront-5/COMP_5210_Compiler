'''
-@author: Tyler Ray
-@date: 8/23/2023

- Tokenizes our input files
- ***WORK IN PROGRESS***

'''
import re


def type_detector(line, character, column_number):

    if character == 'i':
        if not len(line) < column_number + 2:
            word = character + line[column_number + 1] + line[column_number + 2]
            if word == 'int':
                return 'int', 2 # return the type and how many characters we need to skip
        
    elif character == 'c':
        if not len(line) < column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3]
            if word == 'char':
                return 'char', 3
        
    elif character == 'v':
        if not len(line) < column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3]
            if word == 'void':
                return 'void', 3
        
    elif character == 'f':
        if not len(line) < column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4]
            if word == 'float':
                return 'float', 4
        
    elif character == 'd':
        if not len(line) < column_number + 5:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4] + line[column_number + 5]
            if word == 'double':
                return 'double', 5
        
    return False, 0
    


def main(input_file):
    token_specifications = {'symbols': r'(\{|\}|\(|\)|\[|\]|\,|\;|\/|\&|\||\!|\%|\^|\~|\=)',
                            'double_symbols': r'(\=\=|\<\=|\>\=|\!\=|\&\&|\|\||\/\/)',
                            'types': r'(int|float|char|void|double)',
                            'characters': r'([a-zA-Z])'}
    
    tokens = {} #dictionary of tokens, the value is a array with the token and what line number it is found on
    dictionaryIndex = 0
    line_number = 0
    column_number = 0
    skip = False
    multipleSkips = 0

    for line in input_file:
        line = line.strip()
        line_number += 1
        column_number = 0

        for character in line:

            if skip:
                skip = False
                break

            if multipleSkips > 0:
                multipleSkips -= 1
                continue

            elif re.match(token_specifications['symbols'], character):

                if line[-1:] == character:
                    tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]
                else:
                    double_symbol = character + line[column_number + 1]
                    if re.match(token_specifications['double_symbols'], double_symbol):
                        tokens[str(dictionaryIndex)] = ['symbols', double_symbol, line_number, column_number]
                        column_number += 2 # skip the next character since it is part of a double symbol
                        skip = True
                    else: 
                        tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]

            elif re.match(token_specifications['characters'], character):
                type_detection, skip_amount = type_detector(line, character, column_number)
                if type_detection != False:
                    tokens[str(dictionaryIndex)] = ['type', type_detection, line_number, column_number]
                    multipleSkips = skip_amount
                    column_number += skip_amount

            dictionaryIndex += 1
            column_number += 1
    print(tokens)
    return tokens

    


