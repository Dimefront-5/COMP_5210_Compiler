'''
-@author: Tyler Ray
-@date: 8/23/2023

- Tokenizes our input files
- ***WORK IN PROGRESS***

'''
import re

token_specifications = {'symbols': r'(\{|\}|\(|\)|\[|\]|\,|\;|\/|\&|\||\!|\%|\^|\~|\=)',
                            'double_symbols': r'(\=\=|\<\=|\>\=|\!\=|\&\&|\|\||\/\/)',
                            'types': r'(int|float|char|void|double)',
                            'characters': r'([a-zA-Z])',
                            'keywords': r'(if|else|while|for|return|break|continue)'}

def type_detector(line, character, column_number):
    keyword = False
    skip = 0
    if character == 'i':
        if not len(line) <= column_number + 2:
            word = character + line[column_number + 1] + line[column_number + 2]
            if word == 'int' and not re.match(token_specifications['characters'], line[column_number + 3]):
                keyword = 'int'
                skip = 2
        
    elif character == 'c':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3]
            if word == 'char':
                keyword = 'char'
                skip = 3
        
    elif character == 'v':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3]
            if word == 'void':
                keyword = 'void'
                skip = 3
        
    elif character == 'f':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4]
            if word == 'float':
                keyword = 'float'
                skip = 4
        
    elif character == 'd':
        if not len(line) <= column_number + 5:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4] + line[column_number + 5]
            if word == 'double':
                keyword = 'double'
                skip = 5
    
    if keyword != False:
        if not line[column_number + skip] == ' ': #if the type doesn't have a space before and after it isn't a type
            if column_number - 1 >= 0:
                if not line[column_number - 1] == ' ':
                    return keyword, skip # return the type and how many characters to skip
            else:
                return keyword, skip
    return False, 0 # return false if it is not a type
    
def keyword_detector(line, character, column_number):
    keyword = False
    skip = 0
    if character == 'i':
        if not len(line) <= column_number + 1: # Want to avoid OOB error
            word = character + line[column_number + 1]
            if word == 'if':
                keyword = 'if'
                skip = 1
        
    elif character == 'e':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3]
            if word == 'else':
                keyword = 'else'
                skip = 3
        
    elif character == 'w':
        if not len(line) <= column_number + 4:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4]
            if word == 'while':
                keyword = 'while'
                skip = 4
        
    elif character == 'f':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2]
            if word == 'for':
                keyword = 'for'
                skip = 3
        
    elif character == 'r':
        if not len(line) <= column_number + 6:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4] + line[column_number + 5]
            if word == 'return':
                keyword = 'return'
                skip = 6
        
    elif character == 'b':
        if not len(line) <= column_number + 4:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4]
            if word == 'break':
                keyword = 'break'
                skip = 4
        
    elif character == 'c':
        if not len(line) <= column_number + 8:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4] + line[column_number + 5] + line[column_number + 6] + line[column_number + 7]
            if word == 'continue':
                keyword = 'continue'
                skip = 8
    
    if keyword != False:
        if not line[column_number + skip] == ' ':  # if the keyword doesn't have a space after it isn't a keyword
            if column_number - 1 >= 0:
                if not line[column_number - 1] == ' ': #In the case this is a c one liner, we want to make sure the character before is a space or it is invalid
                    return keyword, skip
            else: #if the keyword is at the beginning of the line
                return keyword, skip
        
    return False, 0
    

def main(input_file):
    
    
    tokens = {} #dictionary of tokens, the value is a array with the token and what line number it is found on
    dictionaryIndex = 0
    line_number = 0
    column_number = 0
    skip = 0

    for line in input_file:
        line = line.strip()
        line_number += 1
        column_number = 0

        for character in line:

            if skip > 0:
                skip -= 1
                continue

            elif re.match(token_specifications['symbols'], character):
                
                if len(line) <= column_number + 1: 
                    tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]
                else:
                    double_symbol = character + line[column_number + 1]
                    if re.match(token_specifications['double_symbols'], double_symbol):
                        tokens[str(dictionaryIndex)] = ['symbols', double_symbol, line_number, column_number]
                        column_number += 2 # skip the next character since it is part of a double symbol
                        skip = 1
                    else: 
                        tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]

            elif re.match(token_specifications['characters'], character): # if the character is a letter

                type_detection, skip_amount = type_detector(line, character, column_number) # check if the character is a type
                
                if type_detection != False: # if it is a type
                    tokens[str(dictionaryIndex)] = ['type', type_detection, line_number, column_number]
                    skip = skip_amount
                    column_number += skip_amount # skip the next characters since they are part of a type

                keyword_detection, skip_amount = keyword_detector(line, character, column_number) # check if the character is a keyword

                if keyword_detection != False: # if it is a keyword
                    tokens[str(dictionaryIndex)] = ['keyword', keyword_detection, line_number, column_number]
                    skip = skip_amount
                    column_number += skip_amount # skip the next characters since they are part of a keyword
                

            dictionaryIndex += 1
            column_number += 1
    print(tokens)
    return tokens

    


