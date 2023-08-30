'''
-@author: Tyler Ray
-@date: 8/29/2023

- Tokenizes our input file and returns a dictionary of tokens and their respective types

tokens value = [type, token, line number, column number]
Key is just numbered

- Clarifier: I use github copilot, so some of the code may be generated by it. However most of the code is my ideas and my own work. I used it for most of the tedious work
'''
import re
#Our specifications of tokens
token_specifications = {    'symbols': r'\~|\@|\!|\$|\#|\^|\*|\%|\&|\(|\)|\[|\]|\{|\}|\<|\>|\+|\=|\-|\||\/|\\|\;|\:|\'|\"|\,|\.|\?',
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
def type_modifier_detector(line, character, column_number): 
    keyword = False
    skip = 0

    if character == 's':
        if not len(line) <= column_number + 5: #no OOB error
            word_signed = character + line[column_number +1: column_number+6]

            word_short = character + line[column_number + 1: column_number+5]

            if word_short == 'short':
                keyword = 'short'
                skip = 4

            elif word_signed == 'signed':
                keyword = 'signed'
                skip = 5

    elif character == 'u':
        if not len(line) <= column_number + 7:
            word = character + line[column_number + 1:column_number+8] 

            if word == 'unsigned':
                keyword = 'unsigned'
                skip = 7

    elif character == 'l':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1:column_number + 4]

            if word == 'long':
                keyword = 'long'
                skip = 3        

    if keyword != False and line[column_number + skip + 1] == ' ': #if the type modifier doesn't have a space before and after it isn't a type
        if (column_number - 1) >= 0: #in the case it's the first word in the line
            if line[column_number - 1] == ' ':
                return keyword, skip # return the type and how many characters to skip
        else:
            return keyword, skip
            
    return False, 0

#Will detect any types we have and will return the word if it is a keyword and how many characters to skip
def type_detector(line, character, column_number):
    keyword = False
    skip = 0

    if character == 'i':
        if not len(line) <= column_number + 2:
            word = character + line[column_number + 1:column_number + 3]

            if word == 'int':
                keyword = 'int'
                skip = 2
        
    elif character == 'c':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1:column_number + 4]

            if word == 'char':
                keyword = 'char'
                skip = 3
        
    elif character == 'v':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1:column_number + 4]

            if word == 'void':
                keyword = 'void'
                skip = 3
        
    elif character == 'f':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1:column_number + 5]

            if word == 'float':
                keyword = 'float'
                skip = 4
        
    elif character == 'd':
        if not len(line) <= column_number + 5:
            word = character + line[column_number + 1:column_number + 6]

            if word == 'double':
                keyword = 'double'
                skip = 5
    
    
    if keyword != False and line[column_number + skip + 1] == ' ': #if the type doesn't have a space after it isn't a type
        if (column_number - 1) >= 0:
            if line[column_number - 1] == ' ' or line[column_number - 1] == '(':
                return keyword, skip # return the type and how many characters to skip
        else:
            return keyword, skip
            
    return False, 0 # return false if it is not a type

#Will detect any keywords we have and will return the word if it is a keyword and how many characters to skip
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
            word = character + line[column_number + 1:column_number + 4]

            if word == 'else':
                keyword = 'else'
                skip = 3
        
    elif character == 'w':
        if not len(line) <= column_number + 4:
            word = character + line[column_number + 1:column_number + 4]

            if word == 'while':
                keyword = 'while'
                skip = 4
        
    elif character == 'f':
        if not len(line) <= column_number + 3:
            word = character + line[column_number + 1:column_number + 3]

            if word == 'for':
                keyword = 'for'
                skip = 2
        
    elif character == 'r':
        if not len(line) <= column_number + 6:
            word = character + line[column_number + 1:column_number + 5]
            if word == 'return':
                keyword = 'return'
                skip = 5
        
    elif character == 'b':
        if not len(line) <= column_number + 4:
            word = character + line[column_number + 1:column_number + 4]

            if word == 'break':
                keyword = 'break'
                skip = 4
        
    elif character == 'c':
        if not len(line) <= column_number + 8:
            word = character + line[column_number + 1:column_number + 8]
            if word == 'continue':
                keyword = 'continue'
                skip = 7

    if keyword != False and (line[column_number + skip + 1] == ' ' or line[column_number + skip + 1] == '('): # if the keyword doesn't have a space after it isn't a keyword
        if column_number - 1 >= 0:
            if line[column_number - 1] == ' ': #In the case this is a c one liner, we want to make sure the character before is a space or it is invalid
                return keyword, skip
            
        else: #if the keyword is at the beginning of the line
            return keyword, skip
    return False, 0

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

                    if identifier[i] == '=' or identifier[i] == ' ':
                        skip_amount = i - notskippingthesymbol
                        return identifier[:i], skip_amount
                    
                    elif identifier[i] == '(' and identifier.find(')') > i:
                        skip_amount = i - notskippingthesymbol
                        return identifier[:i], skip_amount
                    else:
                        skip_amount = len(line)
                        return False, skip_amount
                    
                else: #it is a function call or statement, so we want to return the identifier and skip over the symbol
                    skip_amount = i - notskippingthesymbol
                    return identifier[:i], skip_amount
            
    return False, 0

#Our main function for tokenizing any non symbols or numbers. Will look for types, type modifiers, keywords, and identifiers. If none of them are vlaid we will return an error
def character_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex):
    skip = 0

    type_detection, skip_amount_type = type_detector(line, character, column_number) # check if the character is a type
    keyword_detection, skip_amount_keyword = keyword_detector(line, character, column_number) # check if the character is a keyword
    type_modifier_detection, skip_amount_type_modifier = type_modifier_detector(line, character, column_number) # check if the character is a type modifier
    identifier, skip_amount = identifier_detector(line, character, column_number, dict_of_tokens, dictionaryIndex) # check if the character is an identifier

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

    # if it is none of the above, is more than likely invalid Will edit the if statement above to account for errorchecking
    return dict_of_tokens, dictionaryIndex, skip, column_number 

#Will tokenize any characters within single quotes. Will return an error if it is invalid
def char_type_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex):
    skip = 0
    i = column_number + 1 #Don't care about first character since we already know it is a "
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
    dict_of_tokens[str(dictionaryIndex)] = ['symbols', '\'', line_number, column_number + skip + 1] # Go ahead and add the second quotation mark. 
    skip = skip + 1 #We want to skip over the second quotation mark

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

    if i >= len(line): #If we don't find the second quotation mark, it could be on the next line......... or it is an invalid string
        ismultilineString = True
        dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid string', line, line_number, column_number] # A placeholder if we can't find the second quotation mark

        dictionaryIndex += 1
        dict_of_tokens[str(dictionaryIndex)] = ['string', word, line_number, column_number]

        return dict_of_tokens, dictionaryIndex, skip, ismultilineString # we are going to search in the main loop, best way to look through lines
    
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

#Tokenizes our symbols, will also tokenize our comments and strings. Will look out for multiline strings and multiline comments
def symbol_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex):
    #If we hit the symbol tokenizer, we know there is no way it's invalid so we include it in the dictionary
    skip = 0
    comment = False
    multilinestring = False

    if len(line) <= column_number + 1: #We know it isn't a double, so we just add the symbol
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
            dict_of_tokens[str(dictionaryIndex)] = ['symbols', character, line_number, column_number]
            if character == '<' and dict_of_tokens[str(dictionaryIndex - 1)][1] == 'include': #If we have a #include, we want to skip over the entire line
                dictionaryIndex += 1
                dict_of_tokens, dictionaryIndex, skip = include_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex)

            elif character == '\"' and line[column_number -1] != "\\": #Tokenize strings
                dictionaryIndex += 1
                dict_of_tokens, dictionaryIndex, skip, multilinestring = string_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex) #We want to add the entire string as a token
           
            elif character == '\'' and line[column_number - 1] != "\\":
                dict_of_tokens, dictionaryIndex, skip = char_type_tokenizer(line, column_number, line_number, dict_of_tokens, dictionaryIndex)

    return dict_of_tokens, dictionaryIndex, skip, column_number, comment, multilinestring


#validates floats and makes sure they are valid numbers
def float_validator(dict_of_tokens, line, number, dictionaryIndex, line_number, column_number, skip, i):

    decimal_index = i + 1
    while decimal_index < len(number): # we want to go through the rest of the number and make sure it is a valid decimal.

        if number[decimal_index].isdigit(): #If it is a number, we want to continue
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

    if number[2:].isdigit() or re.match(token_specifications['hexidecimal'], number): #If it is a valid hexidecimal, we want to add it
            dict_of_tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
            return dict_of_tokens, skip
        
    
    for i in range(len(number)):
        if re.match(token_specifications['symbols'], number[i]):
            skip = i - 1
            break
    if re.match(token_specifications['hexidecimal'], number[:i]): #If it is a valid hexidecimal, we want to add it
        dict_of_tokens[str(dictionaryIndex)] = ['number', number[:i], line_number, column_number]
        return dict_of_tokens, skip
    else: #If it is an invalid hexidecimal, we want to skip over it
        dict_of_tokens[str(dictionaryIndex)] = ['ERROR: invalid hexidecimal', line, line_number, column_number]
        skip = len(line)
        return dict_of_tokens, skip
    
#Our main number otkenizer, if it shows signs of being a float or hexidecimal, we will call the appropriate function
def number_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex):
    skip = 0
    number = character
    index = column_number + 1
    ishexidecimal = False

    if line[index] == 'x' and line[column_number] == '0': #hexidecmial notation
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
        dict_of_tokens, skip = hexidecmial_validator(dict_of_tokens, line, number, dictionaryIndex, line_number, column_number, skip)
        return dict_of_tokens, skip

    if number.isdigit(): #If the number is a whole valid number just add it and continue
        dict_of_tokens[str(dictionaryIndex)] = ['number', number, line_number, column_number]
        return dict_of_tokens, skip
    
    else: #we are going to go through the entire string until we find a non number character, if it is a symbol. we know that the number is valid and it is an operation with no space
        numberchecker = ''
        for i in range(len(number)):
            numberchecker = numberchecker + number[i]
            if numberchecker.isdigit(): #Continue if it is a valid number
                continue

            elif re.match(token_specifications['symbols'], numberchecker[i]): #Once we hit a symbol, we need to check and see if it a decmial or not
                if number[i] == '.': #double/float detection
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
        
        elif character.isalpha() or character == "_": # if the character is a letter or underscore, to my knowledge underscores are only for identifiers
            dict_of_tokens, dictionaryIndex, skipamount, column_number = character_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex)

        elif re.match(token_specifications['symbols'], character): #I moved this function out for readability
            dict_of_tokens, dictionaryIndex, skipamount, column_number, comment, ismultilinestring = symbol_tokenizer(line, character, column_number, line_number, dict_of_tokens, dictionaryIndex)
        
        elif character.isdigit(): # if the character is a number
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

#used to look for the end of a multiline string
def multiline_string_evalulator(line, line_number, dict_of_tokens, dictionaryIndex, ismultilinestring):
    multilinestring = dict_of_tokens[str(dictionaryIndex -1)][1]

    if '\"' in line:
        multilinestring = multilinestring + line[:line.find('\"')]

        firstquotationIndex = multilinestring.find('\"')

        dict_of_tokens[str(dictionaryIndex -2)] = ['string', multilinestring, line_number, firstquotationIndex + 1] #wnt to override the placeholder error token

        dict_of_tokens[str(dictionaryIndex -1)] = ['symbols', '\"', line_number, line.find('\"')] #add the final " to the tokens

        if line[line.find('\"') + 1] == ')': #hoepfully the string actually ends. 
            dict_of_tokens[str(dictionaryIndex)] = ['symbols', ')', line_number, line.find('\"') + 1]
            dictionaryIndex += 1
        else:
            dict_of_tokens[str(dictionaryIndex - 2)] = ['ERROR: Invalid multiline string', multilinestring, line_number, firstquotationIndex+ 1]
            dictionaryIndex -= 1 #roll the index back and override
            ismultilinestring = False
            return False, dict_of_tokens, dictionaryIndex, line_number

        if line[line.find('\"') + 2] == ';':
            dict_of_tokens[str(dictionaryIndex + 1)] = ['symbols', ';', line_number, line.find('\"') + 2]
            dictionaryIndex += 1
        else:
            dict_of_tokens[str(dictionaryIndex - 2)] = ['ERROR: Invalid multiline string', multilinestring, line_number, firstquotationIndex + 1]
            dictionaryIndex -= 1
            ismultilinestring = False
            return False, dict_of_tokens, dictionaryIndex, line_number
        
        ismultilinestring = False

    else:
        multilinestring = multilinestring + line.strip()
        dict_of_tokens[str(dictionaryIndex)] = ['string', multilinestring, line_number, 0]
        line_number += 1

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
