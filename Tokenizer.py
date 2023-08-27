'''
-@author: Tyler Ray
-@date: 8/27/2023

- Tokenizes our input files
- ***WORK IN PROGRESS***

- Clarifier: I use github copilot, so some of the code may be generated by it. However most of the code is my ideas and my own work. I used it for most of the tedious work
'''
import re

import tokenize

token_specifications = {'symbols': r'\~|\@|\!|\$|\#|\^|\*|\%|\&|\(|\)|\[|\]|\{|\}|\<|\>|\+|\=|\_|\-|\||\/|\\|\;|\:|\'|\"|\,|\.|\?',
                            'double_symbols': r'\=\=|\<\=|\>\=|\!\=|\&\&|\|\||\/\/|\/\*|\*\/|\+\+',
                            'types': r'int|float|char|void|double',
                            'type_modifiers': r'signed|unsigned|long|short',
                            'characters': r'([a-zA-Z])',
                            'keywords': r'if|else|while|for|return|break|continue',
                            'identifiers': r'^[A-Za-z_][\w]*$',
                            'numbers': r'^[\d]+$ | ^[\d]+\.[\d]+$',
                            'hexidecimal': r'^0[xX][\dA-Fa-f]+$'}


def type_modifier_detector(line, character, column_number):
    keyword = False
    skip = 0

    if character == 's':
        if not len(line) <= column_number + 5:
            word_signed = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4] + line[column_number + 5]

            word_short = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4]

            if word_short == 'short':
                keyword = 'short'
                skip = 4

            if word_signed == 'signed':
                keyword = 'signed'
                skip = 5
    elif character == 'u':
        if not len(line) <= column_number + 7:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4] + line[column_number + 5] + line[column_number + 6] + line[column_number + 7]

            if word == 'unsigned':
                keyword = 'unsigned'
                skip = 7
    elif character == 'l':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3]

            if word == 'long':
                keyword = 'long'
                skip = 3        

    if keyword != False:
        if line[column_number + skip + 1] == ' ': #if the type doesn't have a space before and after it isn't a type
            if (column_number - 1) >= 0:
                if line[column_number - 1] == ' ':
                    return keyword, skip # return the type and how many characters to skip
            else:
                return keyword, skip
            
    return False, 0
    
def type_detector(line, character, column_number):
    keyword = False
    skip = 0

    if character == 'i':
        if not len(line) <= column_number + 2:
            word = character + line[column_number + 1] + line[column_number + 2]

            if word == 'int':
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
        if line[column_number + skip + 1] == ' ': #if the type doesn't have a space before and after it isn't a type
            if (column_number - 1) >= 0:
                if line[column_number - 1] == ' ':
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
                skip = 2
        
    elif character == 'r':
        if not len(line) <= column_number + 6:
            word = character + line[column_number + 1] + line[column_number + 2] + line[column_number + 3] + line[column_number + 4] + line[column_number + 5]
            if word == 'return':
                keyword = 'return'
                skip = 5
        
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
                skip = 7

    if keyword != False:
        if line[column_number + skip + 1] == ' ' or line[column_number + skip + 1] == '(': # if the keyword doesn't have a space after it isn't a keyword
            if column_number - 1 >= 0:
                if line[column_number - 1] == ' ': #In the case this is a c one liner, we want to make sure the character before is a space or it is invalid
                    return keyword, skip
                
            else: #if the keyword is at the beginning of the line
                return keyword, skip
    return False, 0

def identifier_detector(line, character, column_number):
    word = character
    column_number += 1
    while (column_number <= (len(line) - 1)) and (not line[column_number] == ' '):
        word = word + line[column_number]
        column_number += 1

    if re.match(token_specifications['identifiers'], word): 
        skip_amount = len(word) - 1
        return word, skip_amount
    else: #If this doesn't match our format, we want to go back through the word and look for special chracters
        i = 0
        for i in range(len(word)):
            if  re.match(token_specifications['symbols'], word[i]):
                skip_amount = i - 1
                return word[:i], skip_amount
    return False, 0
    
def character_adder(line, character, column_number, line_number, tokens, dictionaryIndex):
    skip = 0

    type_detection, skip_amount_type = type_detector(line, character, column_number) # check if the character is a type
    keyword_detection, skip_amount_keyword = keyword_detector(line, character, column_number) # check if the character is a keyword
    type_modifier_detection, skip_amount_type_modifier = type_modifier_detector(line, character, column_number) # check if the character is a type modifier

    if type_modifier_detection != False: # if it is a type modifier
        tokens[str(dictionaryIndex)] = ['type modifier', type_modifier_detection, line_number, column_number]
        skip = skip_amount_type_modifier

    elif type_detection != False: # if it is a type
        tokens[str(dictionaryIndex)] = ['type', type_detection, line_number, column_number]
        skip = skip_amount_type

    elif keyword_detection != False: # if it is a keyword
        tokens[str(dictionaryIndex)] = ['keyword', keyword_detection, line_number, column_number]
        skip = skip_amount_keyword

    else:

        identifier, skip_amount = identifier_detector(line, character, column_number) # check if the character is an identifier
        if identifier != False:
            tokens[str(dictionaryIndex)] = ['identifier', identifier, line_number, column_number]
            skip = skip_amount

    # if it is none of the above, is more than likely invalid Will edit the if statement above to account for errorchecking
    return tokens, dictionaryIndex, skip, column_number 


def string_tokenizer(line, column_number, line_number, tokens, dictionaryIndex):

    skip = 0
    i = column_number + 1 #Don't care about first character since we already know it is a "
    word = ''
    while i < len(line):
        if line[i] == '"':
            break
        else:
            word = word + line[i]
            skip += 1
            i += 1

    dictionaryIndex += 1
    tokens[str(dictionaryIndex)] = ['string', word, line_number, column_number]

    dictionaryIndex += 1
    tokens[str(dictionaryIndex)] = ['symbols', '\"', line_number, column_number + skip + 1] # Go ahead and add the second quotation mark. 
    skip = skip + 1 #We want to skip over the second quotation mark

    return tokens, dictionaryIndex, skip

def symbol_adder(line, character, column_number, line_number, tokens, dictionaryIndex):
    skip = 0
    comment = False

    if len(line) <= column_number + 1: #We know it isn't a double, so we just add the symbol
        tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]


    else:
        double_symbol = character + line[column_number + 1]
        if re.match(token_specifications['double_symbols'], double_symbol):
            tokens[str(dictionaryIndex)] = ['symbols', double_symbol, line_number, column_number]

            if double_symbol == '//': #Skip over comments, they aren't tokens and aren't necessary for our compiler
                skip = len(line) - column_number - 1
            elif double_symbol == '/*': 
                comment = True #don't calculate skip since we will be skipping entire lines
            else:
                skip = 1
            
        else: 
            tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]
            if character == '\"': #Tokenize strings
                tokens, dictionaryIndex, skip = string_tokenizer(line, column_number, line_number, tokens, dictionaryIndex) #We want to add the entire string as a token


    return tokens, dictionaryIndex, skip, column_number, comment



def float_validator(tokens, number, dictionaryIndex, line_number, column_number, skip, i):

    decimal_index = i + 1
    while decimal_index < len(number): # we want to go through the rest of the number and make sure it is a valid decimal.

        if number[decimal_index].isdigit():
            if (decimal_index + 1 == len(number)):
                tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
                skip = len(number) - 1
                return tokens, skip
            decimal_index += 1
        
        elif number[decimal_index] == ' ' or (re.match(token_specifications['symbols'], number[decimal_index]) and not number[decimal_index] == '.'): #If there is a space, then it is a vlaid decimal. Or if there is another symbol but isn't decmial we will say it is valid.
            tokens[str(dictionaryIndex)] = ['number', number[:decimal_index], line_number, column_number]
            skip = len(number[:decimal_index]) - 1
            return tokens, skip
        
        else: #it is an invalid double. We are going to go through the number and find and skip up to the final symbol.
            while decimal_index < len(number):
                if re.match(token_specifications['symbols'], number[decimal_index]):
                    skip = decimal_index -1 #We want to skip over the invalid double
                    break
                else:
                    decimal_index += 1
    
    return tokens, skip

def hexidecmial_validator(tokens, number, dictionaryIndex, line_number, column_number, skip):

    if number[2:].isdigit() or re.match(token_specifications['hexidecimal'], number): #If it is a valid hexidecimal, we want to add it
            tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
            return tokens, skip
        
    elif re.match(token_specifications["symbols"],number[-1:]):
        for i in range(len(number)):
            if re.match(token_specifications['symbols'], number[i]):
                skip = i - 1
                break
        tokens[str(dictionaryIndex)] = ['number', number[:i], line_number, column_number]
        return tokens, skip
    else: #If it is an invalid hexidecimal, we want to skip over it
        return tokens, skip
    
def number_adder(line, character, column_number, line_number, tokens, dictionaryIndex):
    skip = 0
    number = character
    index = column_number + 1
    ishexidecimal = False

    if line[index] == 'x': #hexidecmial notation
        ishexidecimal = True
        number = number + line[index]
        index += 1
        skip += 1
    
    while index < len(line) - 1:
        if line[index] == ' ':
            break
        else:
            number = number + line[index]
            index += 1
            skip += 1

    if ishexidecimal == True: #If it is hexidecimal, we want to make sure it is valid
        tokens, skip = hexidecmial_validator(tokens, number, dictionaryIndex, line_number, column_number, skip)
        return tokens, skip

    if number.isdigit(): #If the number is a whole valid number just add it and continue
        tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
        return tokens, skip
    
    else: #we are going to go through the entire string until we find a non number character, if it is a symbol. we know that the number is valid and it is an operation with no space
        numberchecker = ''
        for i in range(len(number)):
            numberchecker = numberchecker + number[i]
            if numberchecker.isdigit(): #Continue if it is a valid number
                continue

            elif re.match(token_specifications['symbols'], numberchecker[i]): #Once we hit a symbol, we need to check and see if it a decmial or not
                if number[i] == '.': #double/float detection
                    tokens, skip = float_validator(tokens, number, dictionaryIndex, line_number, column_number, skip, i)
                    return tokens, skip
                         
                else: #if it is a random symbol, more than likely it is an assignment and we can just add the number
                    tokens[str(dictionaryIndex)] = ['number', numberchecker[:i], line_number, column_number]
                    skip = len(numberchecker[:i]) - 1
                    return tokens, skip
            else:
                return tokens, skip

    return tokens, 0
    


def tokenizer(line, line_number, tokens, dictionaryIndex, comment):
    column_number = 0
    skipamount = 0

    for character in line:

        if comment == True: #If we are in a comment, we want to skip over the line. Used for multi line comments
            break

        if skipamount > 0:
            skipamount -= 1
            dictionaryIndex -= 1 #Since we are skipping over a character, we want to go back one in the dictionaryIndex since it will be increased at the end
        
        elif re.match(token_specifications['symbols'], character): #I moved this function out for readability
            tokens, dictionaryIndex, skipamount, column_number, comment = symbol_adder(line, character, column_number, line_number, tokens, dictionaryIndex)
        
        elif character.isdigit(): # if the character is a number
            tokens, skipamount = number_adder(line, character, column_number, line_number, tokens, dictionaryIndex)
        
        elif character.isalpha(): # if the character is a letter
            tokens, dictionaryIndex, skipamount, column_number = character_adder(line, character, column_number, line_number, tokens, dictionaryIndex)

        elif character == ' ': #We want to keep dictionary index the same for numbering purposes.
            dictionaryIndex -=1
        
        dictionaryIndex += 1
        column_number += 1
    
    if '*/' in line and comment == True: #We do this after so we can skip over the final line
        tokens[str(dictionaryIndex)] = ['symbols', '*/', line_number, len(line) - 2]  #add the final */ to the tokens
        comment = False
        dictionaryIndex += 1

    return tokens, dictionaryIndex, comment


def main(input_file):

    tokens = {} #dictionary of tokens, the value is a list as follows [type, token, line number, column number]
    dictionaryIndex = 0
    line_number = 0
    comment = False

    for line in input_file:
        line_number += 1
        line = line.strip()
        tokens, dictionaryIndex, comment = tokenizer(line, line_number, tokens, dictionaryIndex, comment)

    return tokens
