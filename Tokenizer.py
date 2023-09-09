'''
-@author: Tyler Ray
-@date: 9/9/2023

- Tokenizes our input file and returns a dictionary of tokens and their respective types

tokens value = [type, token, line number, column number]
Key = [0, n]

- Clarifier: I use github copilot, so some of the code may be generated by it. However most of the code is my ideas and my own work. I used it for most of the tedious work
'''

import re
#Our specifications of tokens
token_specifications = {    'symbols': r'\~|\@|\!|\$|\#|\^|\*|\%|\&|\(|\)|\[|\]|\{|\}|\<|\>|\+|\=|\-|\||\/|\\|\;|\:|\'|\"|\,|\.|\?',
                            'mulOP': r'\*|\/|\%',
                            'addOP': r'\+|\-',
                            'double_symbols': r'\=\=|\<\=|\>\=|\!\=|\&\&|\|\||\/\/|\/\*|\*\/|\+\+|\-\-',
                            'types': r'int|float|char|void|double',
                            'type_modifiers': r'signed|unsigned|long|short',
                            'characters': r'([a-zA-Z])',
                            'keywords': r'if|else|while|for|return|break|continue',
                            'identifiers': r'^[A-Za-z_][\w_]*$',
                            'numbers': r'^[\d]+$ | ^[\d]+\.[\d]+$',
                            'hexidecimal': r'^0[xX][\dA-Fa-f]+$',
                            'include': r'^[A-Za-z_]*[.][h]$'}

#Will detect any type modifiers we have and will return the word if it is a keyword and how many characters to skip
def type_modifier_detector(line, column_number): 
    keyword = False
    skip = 0

    word = word_creator(line, column_number, 8)

    if word[0:5] == 'short':
        keyword = 'short'
        skip = 4
    
    elif word[0:6] == 'signed':
        keyword = 'signed'
        skip = 5

    elif word[0:8] == 'unsigned':
        keyword = 'unsigned'
        skip = 7

    elif word[0:4] == 'long':
        keyword = 'long'
        skip = 3        

    if keyword != False and line[column_number + skip + 1] == ' ': #if the type modifier doesn't have a space before and after it isn't a type
        if (column_number - 1) >= 0: #in the case it's the first word in the line
            if line[column_number - 1] == ' ':
                return keyword, skip
        else:
            return keyword, skip
            
    return False, 0

#Will detect any types we have and will return the word if it is a keyword and how many characters to skip
def type_detector(line, column_number):
    keyword = False
    word = word_creator(line, column_number, 6)

    if word[0:3] == 'int':
        keyword = 'int'
        skip = 2
        
    elif word[0:4] == 'char':
        keyword = 'char'
        skip = 3
        
    elif word[0:4] == 'void':
        keyword = 'void'
        skip = 3
        
    elif word[0:5] == 'float':
        keyword = 'float'
        skip = 4
        
    elif word[0:6] == 'double':
        keyword = 'double'
        skip = 5
    
    if keyword != False and line[column_number + skip + 1] == ' ': #if the type doesn't have a space after it isn't a type
        if (column_number - 1) >= 0:
            if line[column_number - 1] == ' ' or line[column_number - 1] == '(':
                return keyword, skip
        else:
            return keyword, skip
            
    return False, 0 # return false if it is not a type

#Will detect any keywords we have and will return the word if it is a keyword and how many characters to skip
def keyword_detector(line, column_number):
    keyword = False
    skip = 0

    word = word_creator(line, column_number, 8)

    if word[0:2] == 'if':
        keyword = 'if'
        skip = 1
        
    elif word[0:4] == 'else':
        keyword = 'else'
        skip = 3
        
    elif word[0:5] == 'while':
        keyword = 'while'
        skip = 4
        
    elif word[0:3] == 'for':
        keyword = 'for'
        skip = 2
        
    elif word[0:6] == 'return':
        keyword = 'return'
        skip = 5
        
    elif word[0:5] == 'break':
        keyword = 'break'
        skip = 4
        
    elif word[0:8] == 'continue':
        keyword = 'continue'
        skip = 7

    if keyword != False and (line[column_number + skip + 1] == ' ' or line[column_number + skip + 1] == '('): # if the keyword doesn't have a space after it isn't a keyword
        if column_number - 1 >= 0:
            if line[column_number - 1] == ' ': #In the case this is a c one liner, we want to make sure the character before is a space or it is invalid
                return keyword, skip
            
        else: #if the keyword is at the beginning of the line
            return keyword, skip
        
    return False, 0

#Will walk through the line and create a word based on the maximum length that is allowed
def word_creator(line, column_number, total_length_of_allowed_word):
    skip = 0
    i = column_number
    word = ''

    while skip < total_length_of_allowed_word: #We want to go through the entire type length and add it to a string, we want to make sure we can hit the shorter words
        if i >= len(line):
            break

        word = word + line[i]
        i += 1
        skip += 1

    return word

#checks when we see a type before an identifier and validates it is a valid way to call a function or decleration
def check_for_type(identifier, i, notskippingthesymbol, line):
    if identifier[i] == '=' or identifier[i] == ' ':
        skip_amount = i - notskippingthesymbol
        return identifier[:i], skip_amount
    
    elif identifier[i] == '(' and identifier.find(')') > i:
        skip_amount = i - notskippingthesymbol
        return identifier[:i], skip_amount
    else:
        skip_amount = len(line)
        return False, skip_amount
    
#Will evaluate if the identifier is valid or not then return the valid identifer and how many characters to skip over or False if it isn't one
def identifier_detector(line, character, column_number, dict_of_tokens, dictionaryIndex):
    identifier = character
    column_number += 1
    notskippingthesymbol = 1 

    while (column_number <= (len(line) - 1)) and (not line[column_number] == ' '):
        identifier = identifier + line[column_number]
        column_number += 1

    if re.match(token_specifications['identifiers'], identifier): 
        skip_amount = len(identifier) - 1
        return identifier, skip_amount
    
    else: #If this doesn't match our format, we want to go back through the word and look for special chracters and see if it is being called within a function or statement
        i = 0
        for i in range(len(identifier)):

            if  re.match(token_specifications['symbols'], identifier[i]):
                
                if dict_of_tokens[str(dictionaryIndex-1)][0] == 'type': #decleration, we need to account for function names
                    identifier, skip_amount = check_for_type(identifier, i, notskippingthesymbol, line)
                    return identifier, skip_amount 
                    
                else: #it is a function call or statement, so we want to return the identifier and skip over the symbol
                    skip_amount = i - notskippingthesymbol
                    return identifier[:i], skip_amount
            
    return False, 0

#Our main function for tokenizing any non symbols or numbers. Will look for types, type modifiers, keywords, and identifiers. If none of them are vlaid we will return an error
def character_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex):
    skip = 0

    type_detection, skip_amount_type = type_detector(line, column_number)
    keyword_detection, skip_amount_keyword = keyword_detector(line, column_number) 
    type_modifier_detection, skip_amount_type_modifier = type_modifier_detector(line, column_number) 
    identifier, skip_amount = identifier_detector(line, character, column_number, dict_of_tokens, dictionaryIndex) 

    if type_modifier_detection != False: # if it is a type modifier
        dict_of_tokens[str(dictionaryIndex)] = ['type modifier', type_modifier_detection, line_number, column_number]
        skip = skip_amount_type_modifier

    elif type_detection != False: # if it is a type
        dict_of_tokens[str(dictionaryIndex)] = ['type', type_detection, line_number, column_number]
        skip = skip_amount_type

    elif keyword_detection != False: # if it is a keyword
        dict_of_tokens[str(dictionaryIndex)] = ['keyword', keyword_detection, line_number, column_number]
        skip = skip_amount_keyword

    elif identifier != False:
            dict_of_tokens[str(dictionaryIndex)] = ['identifier', identifier, line_number, column_number]
            skip = skip_amount
    else: #None of the above, return this error
        dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid identifier', line, line_number, column_number]
        skip = len(line)

    return dict_of_tokens, dictionaryIndex, skip, column_number 

#Will tokenize any characters within single quotes. Will return an error if it is invalid
def char_type_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex):
    skip = 0
    i = column_number + 1 
    word = ''
    while i < len(line):
        if line[i] == '\'' and line[i-1] != '\\': #want to make sure it isn't an escaped quotation mark
            break
        else:
            word = word + line[i]
            skip += 1
            i += 1

    if i >= len(line): #If we don't find the second quotation mark, we know it is an invalid string
        dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid characters', line, line_number, column_number]
        return dict_of_tokens, dictionaryIndex, skip
    
    dictionaryIndex += 1
    dict_of_tokens[str(dictionaryIndex)] = ['characters', word, line_number, column_number + 1]

    dictionaryIndex += 1
    dict_of_tokens[str(dictionaryIndex)] = ['symbols', '\'', line_number, column_number + skip + 1] 
    skip = skip + 1 

    return dict_of_tokens, dictionaryIndex, skip

#Tokenizes our entire strings into a single token
def string_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex):
    ismultilineString = False
    skip = 0
    i = column_number + 1 #Don't care about first character since we already know it is a "
    word = ''
    while i < len(line):
        if line[i] == '"' and line[i-1] != '\\': #want to make sure it isn't an escaped quotation mark
            break
        else:
            word = word + line[i]
            skip += 1
            i += 1

    if i >= len(line):
        dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid string', line, line_number, column_number] # A placeholder if we can't find the second quotation mark

        if line[-1] == '\\': #If the last character is a backslash, we know it is a multiline string
            ismultilineString = True
            dictionaryIndex += 1
            dict_of_tokens[str(dictionaryIndex)] = ['string', word, line_number, column_number]

        return dict_of_tokens, dictionaryIndex, skip, ismultilineString
    
    dictionaryIndex += 1
    dict_of_tokens[str(dictionaryIndex)] = ['string', word, line_number, column_number]

    dictionaryIndex += 1
    dict_of_tokens[str(dictionaryIndex)] = ['symbols', '\"', line_number, column_number + skip + 1] # Go ahead and add the second quotation mark. 
    skip = skip + 1 #We want to skip over the second quotation mark

    return dict_of_tokens, dictionaryIndex, skip, ismultilineString

#Tokenizes our include statement, only the header file name
def include_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex):
    skip = 0
    i = column_number + 1 #Don't care about first character since we already know it is a <
    word = ''
    while i < len(line):
        if line[i] == '>':
            break
        else:
            word = word + line[i]
            skip += 1
            i += 1

    if i >= len(line): #If we don't find the second symbol, we know it is an invalid include statement
        dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid include statement', line, line_number, column_number]
        skip = len(line)
        return dict_of_tokens, dictionaryIndex, skip
    
    if re.match(token_specifications['include'], word): #If it is a valid identifier, we want to add it
        dict_of_tokens[str(dictionaryIndex)] = ['include header', word, line_number, column_number + 1]

    else: #invalid include statement
        dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid include statement', line, line_number, column_number]
        skip = len(line)
        return dict_of_tokens, dictionaryIndex, skip
    
    dictionaryIndex += 1
    return dict_of_tokens, dictionaryIndex, skip

#Will look for any special starting tokens, such as #include, "strings, and characters
def looking_for_special_starting_tokens(line, column_number, line_number, dict_of_tokens, dictionaryIndex):
    multilinestring = False
    skip = 0
    character = line[column_number]
    if character == '<' and dict_of_tokens[str(dictionaryIndex - 1)][1] == 'include': #If we have a #include, we want to skip over the entire line
        dictionaryIndex += 1
        dict_of_tokens, dictionaryIndex, skip = include_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex)

    elif character == '\"' and line[column_number -1] != "\\": #Tokenize strings
        dictionaryIndex += 1
        dict_of_tokens, dictionaryIndex, skip, multilinestring = string_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex) #We want to add the entire string as a token
    
    elif character == '\'' and line[column_number - 1] != "\\":
        dict_of_tokens, dictionaryIndex, skip = char_type_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex)


    return dict_of_tokens, dictionaryIndex, skip, multilinestring

#Tokenizes our symbols, will also tokenize our comments and strings. Will look out for multiline strings and multiline comments
def symbol_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex):
    skip = 0
    comment = False
    multilinestring = False

    if len(line) <= column_number + 1:
        dict_of_tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]

    else: #Double symbol detection
        double_symbol = character + line[column_number + 1]
        if re.match(token_specifications['double_symbols'], double_symbol):
            dict_of_tokens[str(dictionaryIndex)] = ['symbols', double_symbol, line_number, column_number]

            if double_symbol == '//': #Skip over comments, they aren't tokens and aren't necessary for our compiler
                skip = len(line) - column_number - 1
            elif double_symbol == '/*': 
                comment = True #don't calculate skip since we will be skipping entire lines
            else:
                skip = 1
            
        else:
            if re.match(token_specifications['mulOP'], character) and dict_of_tokens[str(dictionaryIndex - 1)][0] != 'type': #want to allow for pointers and not think of it as a mulOP
                dict_of_tokens[str(dictionaryIndex)] = ['mulOP', character, line_number, column_number]
                
            elif re.match(token_specifications['addOP'], character):
                dict_of_tokens[str(dictionaryIndex)] = ['addOP', character, line_number, column_number]

            else:
                dict_of_tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]
                dict_of_tokens, dictionaryIndex, skip, multilinestring = looking_for_special_starting_tokens(line, column_number, line_number, dict_of_tokens, dictionaryIndex)
            
    return dict_of_tokens, dictionaryIndex, skip, column_number, comment, multilinestring


#validates floats and makes sure they are valid numbers
def float_validator(dict_of_tokens, line, number, dictionaryIndex, line_number, column_number, skip, i):

    decimal_index = i + 1
    while decimal_index < len(number): # we want to go through the rest of the number and make sure it is a valid decimal.

        if number[decimal_index].isdigit():
            if (decimal_index + 1 == len(number)): #If the number is at the end of the string, we want to add it
                dict_of_tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
                skip = len(number) - 1
                return dict_of_tokens, skip
            
            decimal_index += 1
        
        elif number[decimal_index] == ' ' or (re.match(token_specifications['symbols'], number[decimal_index]) and not number[decimal_index] == '.'): #If there is a space, then it is a vlaid decimal. Or if there is another symbol but isn't decmial we will say it is valid.
            dict_of_tokens[str(dictionaryIndex)] = ['number', number[:decimal_index], line_number, column_number]
            skip = len(number[:decimal_index]) - 1
            return dict_of_tokens, skip
        
        else: #it is an invalid double. We are going to go through the number and find and skip up to the final symbol.
            while decimal_index < len(number):

                if re.match(token_specifications['symbols'], number[decimal_index]) or re.match(token_specifications['characters'], number[decimal_index]):
                    dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid double', line, line_number, column_number]

                    skip = len(line)
                    return dict_of_tokens, skip
                else:
                    decimal_index += 1
    
    return dict_of_tokens, skip

#validates hexidecmials and makes sure they are valid numbers
def hexidecmial_validator(dict_of_tokens, line,  number, dictionaryIndex, line_number, column_number, skip):

    if number[2:].isdigit() or re.match(token_specifications['hexidecimal'], number):
            dict_of_tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
            return dict_of_tokens, skip
        
    
    for i in range(len(number)):
        if re.match(token_specifications['symbols'], number[i]):
            skip = i - 1
            break
    if re.match(token_specifications['hexidecimal'], number[:i]):
        dict_of_tokens[str(dictionaryIndex)] = ['number', number[:i], line_number, column_number]
        return dict_of_tokens, skip
    else: 
        dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid hexidecimal', line, line_number, column_number]
        skip = len(line)
        return dict_of_tokens, skip


#goes through a nonvalid number and looks for first symbol to see if it is being used within a operation or if it is an assignment
def looking_for_first_non_number(line, column_number, line_number, dict_of_tokens, dictionaryIndex, number, skip):
    numberchecker = ''
    for i in range(len(number)):
        numberchecker = numberchecker + number[i]
        if numberchecker.isdigit():
            continue

        elif re.match(token_specifications['symbols'], numberchecker[i]): #Once we hit a symbol, we need to check and see if it a decmial or not
            if number[i] == '.':
                dict_of_tokens, skip = float_validator(dict_of_tokens, line, number, dictionaryIndex, line_number, column_number, skip, i)
                return dict_of_tokens, skip
                        
            else: #if it is a random symbol, more than likely it is an assignment and we can just add the number
                dict_of_tokens[str(dictionaryIndex)] = ['number', numberchecker[:i], line_number, column_number]
                skip = len(numberchecker[:i]) - 1
                return dict_of_tokens, skip
        else:
            dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid number', line, line_number, column_number]
            skip = len(line)
            return dict_of_tokens, skip
        
    return dict_of_tokens, 0
    
#Our main number otkenizer, if it shows signs of being a float or hexidecimal, we will call the appropriate function
def number_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex):
    skip = 0
    number = character
    index = column_number + 1
    ishexidecimal = False

    if len(line) <= column_number + 1:
        dict_of_tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
        return dict_of_tokens, skip
    
    if line[index] == 'x' and line[column_number] == '0': #hexidecmial notation
        ishexidecimal = True
        number = number + line[index]
        index += 1
        skip += 1

    while index < len(line):
        if line[index] == ' ':
            break
        else:
            number = number + line[index]
            index += 1
            skip += 1

    if ishexidecimal == True: #If it is hexidecimal, we want to make sure it is valid
        dict_of_tokens, skip = hexidecmial_validator(dict_of_tokens, line, number, dictionaryIndex, line_number, column_number, skip)
        return dict_of_tokens, skip

    if number.isdigit(): #If the number is a whole valid number just add it and continue
        dict_of_tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
        return dict_of_tokens, skip
    
    else: #we are going to go through the entire string until we find a non number character, if it is a symbol. we know that the number is valid and it is an operation with no space
        dict_of_tokens, skip = looking_for_first_non_number(line, column_number, line_number, dict_of_tokens, dictionaryIndex, number, skip)
        return dict_of_tokens, skip
        

# Our overall main tokenizer function, calls the appropriate functions for tokenizing depending on the character it is given. Skips over whitespaces
def main_tokenizer(line, line_number, dict_of_tokens, dictionaryIndex, comment):
    column_number = 0
    skipamount = 0
    ismultilinestring = False

    for character in line:

        if comment == True: #If we are in a comment, we want to skip over the line. Used for multi line comments
            break

        if skipamount > 0:
            skipamount -= 1
            dictionaryIndex -= 1 #Since we are skipping over a character, we want to go back one in the dictionaryIndex since it will be increased at the end
        
        elif character.isalpha() or character == "_":
            dict_of_tokens, dictionaryIndex, skipamount, column_number = character_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex)

        elif re.match(token_specifications['symbols'], character):
            dict_of_tokens, dictionaryIndex, skipamount, column_number, comment, ismultilinestring = symbol_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex)
        
        elif character.isdigit():
            dict_of_tokens, skipamount = number_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex)

        elif character == ' ': #We want to keep dictionary index the same for numbering purposes.
            dictionaryIndex -=1
        
        dictionaryIndex += 1
        column_number += 1
    
    if '*/' in line and comment == True: #We do this after so we can skip over the final line
        dict_of_tokens[str(dictionaryIndex)] = ['symbols', '*/', line_number, len(line) - 2]  #add the final */ to the tokens
        comment = False
        dictionaryIndex += 1

    return dict_of_tokens, dictionaryIndex, comment, ismultilinestring


#validating the end of ourmultiline has a ); we do not allow for string formatting on multilines
def end_of_multiline_validation(line, line_number, dict_of_tokens, dictionaryIndex, multilinestring, firstquotationIndex):

    if line[line.find('\"') + 1] == ')':
        dict_of_tokens[str(dictionaryIndex)] = ['symbols', ')', line_number, line.find('\"') + 1]
        dictionaryIndex += 1
    else:
        dict_of_tokens[str(dictionaryIndex - 2)] = ['ERROR: Invalid multiline string', multilinestring, line_number, firstquotationIndex+ 1]
        dictionaryIndex -= 1 #roll the index back and override
        return dict_of_tokens, dictionaryIndex, line_number

    if line[line.find('\"') + 2] == ';':
        dict_of_tokens[str(dictionaryIndex + 1)] = ['symbols', ';', line_number, line.find('\"') + 2]
        dictionaryIndex += 1
    else:
        dict_of_tokens[str(dictionaryIndex - 2)] = ['ERROR: Invalid multiline string', multilinestring, line_number, firstquotationIndex + 1]
        dictionaryIndex -= 1
        return dict_of_tokens, dictionaryIndex, line_number
    
    return dict_of_tokens, dictionaryIndex, line_number
    
#used to look for the end of a multiline string
def multiline_string_evalulator(line, line_number, dict_of_tokens, dictionaryIndex, ismultilinestring):
    multilinestring = dict_of_tokens[str(dictionaryIndex -1)][1].strip()
    line=line.strip()

    if '\"' in line:
        multilinestring = multilinestring + line[:line.find('\"')]

        firstquotationIndex = multilinestring.find('\"')

        dict_of_tokens[str(dictionaryIndex -2)] = ['string', multilinestring, line_number, firstquotationIndex + 1] #want to override the placeholder error token

        dict_of_tokens[str(dictionaryIndex -1)] = ['symbols', '\"', line_number, line.find('\"')] #add the final " to the tokens
        
        ismultilinestring = False

        dict_of_tokens, dictionaryIndex, line_number = end_of_multiline_validation(line, line_number, dict_of_tokens, dictionaryIndex, multilinestring, firstquotationIndex)

    elif line[-1:] == '\\': #if the last character is a backslash, we know it is a multiline string:
        multilinestring = multilinestring + line.strip()
        dict_of_tokens[str(dictionaryIndex - 1)] = ['string', multilinestring, line_number, 0]
        line_number += 1

    else:
        dict_of_tokens[str(dictionaryIndex - 2)] = ['ERROR: Invalid multiline string', multilinestring, line_number, 0]
        dictionaryIndex -= 1
        line_number += 1
        ismultilinestring = False

    return ismultilinestring, dict_of_tokens, dictionaryIndex, line_number
        
#Our main function that starts our tokenizer
def main(input_file):

    dict_of_tokens = {} #dictionary of tokens, the value is a list as follows [type, token, line number, column number]
    dictionaryIndex = 0
    line_number = 0
    comment = False
    ismultilinestring = False

    for line in input_file:

        if ismultilinestring == True:
            ismultilinestring, dict_of_tokens, dictionaryIndex, line_number = multiline_string_evalulator(line, line_number, dict_of_tokens, dictionaryIndex, ismultilinestring)
            continue
        
        line_number += 1
        line = line.strip()
        dict_of_tokens, dictionaryIndex, comment, ismultilinestring = main_tokenizer(line, line_number, dict_of_tokens, dictionaryIndex, comment)

    return dict_of_tokens
