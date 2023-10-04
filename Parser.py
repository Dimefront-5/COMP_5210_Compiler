'''
-@author: Tyler Ray
-@date: 10/3/2023

- Will parse through our token list and output a AST along with a symbol table
- Works for the below grammar
'''
import CompilerConstants as cc
from anytree import RenderTree #Our fancy printing with AST
import re
import sys

#grammar for our parser
#A capital first letter symbolizes a non-terminal, a lowercase first letter symbolizes a literal token
#Some of the backslashes are used freely, none of this grammar uses a literal backslash
grammar = {
    'Program': ['DeclList'],
    'DeclList': ['Decl', 'Decl DeclList'],
    'Decl': ['Type id (Args) \{Local_Decls stmtList\}, Type id = endofDecl;'],

    'Args': ['Arg', 'Arg\, Args'],
    'Arg': ['Type id', ''], #No tpye modifier and type for args

    'Local_Decls': ['Local_Decl', 'Local_Decl Local_Decls'],
    'Local_Decl': ['TypeModifier (*)Type id;', 'TypeModifier Type (*)id = EndOfDecl;',''],#This also turns into just type id = endofDecl; or type id; Since typemodifier can be empty
        #The (*) means that it can be optional
        
    'StmtList': ['Stmt', 'Stmt StmtList'],
    'Stmt': ['ReturnStmt', 'AssignStmt', 'WhileStmt', 'IfStmt', 'FunctionCall' ,''],

    'ReturnStmt': ['return num;', 'return id;', 'return;', 'return expr;', 'return character', 'return string'],
    'AssignStmt': ['id = EndOfDecl;'],
    'WhileStmt': ['while (Conditional_Exprs) \{StmtList\}'],
    'IfStmt': ['if (Conditional_Exprs) \{StmtList\}', 'if (Conditional_Expr) \{StmtList\} else \{StmtList\}'],
    'FunctionCall': ['id(Params);'],

    'Params': ['Param', 'Param\, Params'],
    'Param': ['Expr', 'string', 'character'],

    'Condtional_Exprs': ['Conditional_Expr', 'Conditional_Expr && Conditional_Exprs', 'Conditional_Expr || Conditional_Exprs'],
    'Conditional_Expr': ['Expr Relop Expr'],
    'Relop': [r'^==$|^!=$|^>$|^>=$|^<$|^<=$'],

    'EndOfDecl': ['Expr', 'string', 'character'],

    'Expr': ['Term + Expr', 'Term - Expr', 'Term'],
    'Term': ['Factor * Term', 'Factor / Term', 'Factor'],
    'Factor': ['num', '(Expr)', 'id'],

    'Type': ['NumType', 'void', 'char', 'TypeModifier'],
    'NumType': [r'double|int|float'],
    'TypeModifiersToBegin': ['TypeModifier', ''], #I had to break it up like this so when a type picks a typemodifier, it can't go to empty and then we have no type
    'TypeModifier': [r'signed|unsigned|long|short'],

    'string': [r'^"[^"]*"$'],
    'character': ['\'[a-zA-Z]\''],
    'num': [r'^[\d]+$ | ^[\d]+\.[\d]+$'],
    'id': [r'^[A-Za-z_][\w_]*$'] 
}

#SymbolTable class ----------------
#I had chatGPT generate this for me, I wrote most of it before hand and had it refine it
class SymbolTable:
    def __init__(self):
        self.symbolTable = {}   #dictionary of dictionaries, first key is the scope, with a value of a dictionary of variables and their types. Second variable is return variables
    #example: {'parser': {'x': 'int', 'y': 'float'}, 'main': {'z': 'int'}

    def get_type(self, name, scope):
        if scope in self.symbolTable and name in self.symbolTable[scope]:
            return self.symbolTable[scope][name]
        else:
            return None  # Handle the case when the variable is not found

    def get_scope_type(self, scope):
        if scope in self.symbolTable:
            return self.symbolTable[scope]['return_type']
        else:
            return None
    
    def add_variable(self, name, type, scope):
        self.symbolTable[scope][name] = [type]

    def add_scope(self, scope, fun_type, params):
        if scope not in self.symbolTable:
            self.symbolTable[scope] = {}  # Create a new scope
        self.symbolTable[scope]['return_type'] = fun_type
        self.symbolTable[scope]['args'] = params

    def get_args(self, scope):
        if scope in self.symbolTable:
            return self.symbolTable[scope]['args']
        else:
            return None

    def add_value(self, name, value, scope):
        if name in self.symbolTable[scope]:
            self.symbolTable[scope][name] = [self.symbolTable[scope][name][0], value]
        else:
            self.symbolTable[scope][name].append(value)


    def __str__(self):
        output = ""
        for scope in self.symbolTable:
            output += "Scope: " + scope + "\n\t" + "Return Type: " + self.symbolTable[scope]['return_type'] + "\n\tArguments: " + str(self.symbolTable[scope]['args']) + "\n"
            output += "\tVariables:\n"

            for variable in self.symbolTable[scope]:

                if variable != 'return_type' and variable != 'args':
                    output += "\t\t" + variable + ": " + self.symbolTable[scope][variable][0]

                    if len(self.symbolTable[scope][variable]) > 1:
                        output += " = " + str(self.symbolTable[scope][variable][1])
                        output += "\n"
                    else:
                        output += "\n"
            output += "\n"
        return output
    
#ASTNode class ----------------
#I had chatGPT generate this for me
class ASTNode:
    def __init__(self, value=None):
        self.value = value          
        self.children = [] # List of child nodes

    def add_child(self, child_node):
        self.children.append(child_node)

    def __str__(self):
        output = ""
        for pre, fill, node in RenderTree(self):
            output += "%s%s" % (pre, node.value) + "\n"
        return output
    
    def return_children(self):
        return self.children
    
    def return_value(self):
        return self.value
    


global index
index = 0
global symbolTable
symbolTable = SymbolTable()
global scope
scope = "global"

#main function for the parser
def parser(tokens):
    symbolTable.add_scope('global', 'void', None) #We want to make sure always have a global scope

    parseTree = _parseProgram(tokens)

    return parseTree, symbolTable

#----- Inward facing modules

#_customError function ----------------
#Will take a list of tokens and the index of the token that caused the error and return a string with the error message pointing to the issue
#I may eventually want to push this to it's own file to use across the compiler. For now, it will be located here
#I had github copilot generate this for me.
def _customError(message, tokens, index):
    #first we want to find the line number of the token that caused the error
    line_number = tokens[str(index)][cc.LINE_NUMBER_INDEX]
    #now we want to take every token within that line number and combine it into a string
    line = ''
    for keyIndex in tokens:
        if tokens[keyIndex][cc.LINE_NUMBER_INDEX] == line_number:
            line += tokens[keyIndex][cc.TOKEN_INDEX] + ' '

    #Now we want to take the column number of the issue and point an arrow to it
    column_number = tokens[str(index)][cc.COLUMN_NUMBER_INDEX]
    arrow = ''
    for i in range(column_number):
        arrow += ' '
    arrow += '^'
    
    #Now we want to combine the line and the arrow and the message
    line += '\n' + arrow
    line += '\n' + message + ' on line ' + str(line_number) + ', column ' + str(column_number)

    print(line)
    sys.exit()


#The start of parsing our program ----------------

#program -> declList
def _parseProgram(tokens):
    programNode = ASTNode("Program")
    global index

    while index < len(tokens): # we want to parse until we hit the end of the tokens
        programNode.add_child(_parseDeclList(tokens))
        index +=1

    return programNode

#declList -> decl declList | decl
def _parseDeclList(tokens, declListNode = ASTNode("declList")):
    global scope

    declNode = _parseDecl(tokens)

    if declNode == None:
        _customError("Error: Invalid decl", tokens, index)
    
    scope = "global" #We want to reset the scope to global after we are done with a function

    if index < len(tokens) and tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        declListNode2 = _parseDeclList(tokens, declListNode)
        declListNode2.add_child(declNode)
        return declListNode2
    
    else:
        declListNode.add_child(declNode)
    

    return declListNode

#decl -> type id (Args) {local_decls stmtList} | type id = endofDecl;
def _parseDecl(tokens):
    declNode = ASTNode("decl")

    global index
    global scope
    errormsg = 'Error: Invalid decl'

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        typeNode = ASTNode("type")
        declType = tokens[str(index)][cc.TOKEN_INDEX]
        typeNode.add_child(ASTNode(declType))

        index += 1
        
        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            idNode = ASTNode("id")
            declId = tokens[str(index)][cc.TOKEN_INDEX]
            idNode.add_child(ASTNode(declId))

            
            index += 1
            errormsg = 'Error: Invalid decl, expected \'(\' or \'=\''

            if tokens[str(index)][cc.TOKEN_INDEX] == '(': #It is a function decl
                declNode = _functionDecl(tokens, idNode, typeNode, declNode)
                return declNode
                        
            elif tokens[str(index)][cc.TOKEN_INDEX] == '=': #It is a global variable, so we can just parse the back of it using endofDecl_parser

                global_decl = _parseEndofDecl(tokens, idNode, declType, declId)
                if global_decl != None:
                    declNode.add_child(global_decl)
                    return declNode
                
    _customError(errormsg, tokens, index)

#decl -> type id (Args) {local_decls stmtList}
def _functionDecl(tokens, idNode, typeNode, declNode):
    global index
    global scope

    scope_type = tokens[str(index-2)][cc.TOKEN_INDEX]
    scope = tokens[str(index-1)][cc.TOKEN_INDEX]

    declNode.add_child(idNode)
    declNode.add_child(typeNode)


    declNode, args = _parseArgsSetup(tokens, declNode) #We want to parse through our args and add them to our symbol table for our function
    symbolTable.add_scope(scope, scope_type, args)

    errormsg = 'Error: Invalid decl, expected \')\''

    if tokens[str(index)][cc.TOKEN_INDEX] == ')':

        index += 1
        errormsg = 'Error: Invalid decl, expected \'{\''

        if tokens[str(index)][cc.TOKEN_INDEX] == '{':

            declNode = _parseInFunction(tokens, declNode) #Used to parse through our local_decls and stmtList

            errormsg = 'Error: Invalid decl, expected \'}\''

            if tokens[str(index)][cc.TOKEN_INDEX] == '}':
                index += 1
                return declNode
        else:
            index -= 1 #We want to go back to the previous token so we can get a better error message

    _customError(errormsg, tokens, index)

#start of args parser ----------------

#staging for parse args, just creating a overall args node to pass in, then checking to see if there are any args
#We have this so so we can add each node to the main args node, and then add the main args node to the decl node
def _parseArgsSetup(tokens, declNode):
    global index

    index += 1
    argsNode = ASTNode("Args")
    
    argsNode, args = (_parseArgs(tokens, argsNode))

    if argsNode != None: #don't add args if there are no args
        declNode.add_child(argsNode)

    return declNode, args

#Args -> Arg, Args | Arg
def _parseArgs(tokens, argsNode):
    global index

    argNode1, initialArgs = _parseOneArg(tokens)

    if tokens[str(index)][cc.TOKEN_INDEX] == ',':#Looking to see if there are multiple args |  ',' is our indicator
        index += 1
        argNode2, args = _parseArgs(tokens, argsNode)

        initialArgs.update(args) #We want to gather all of the args to add to the function scope, we pass them back so we can add all at once
        argNode2.add_child(argNode1)

        return argNode2, initialArgs
    
    else: #if no more args
        argsNode.add_child(argNode1)
        return argsNode, initialArgs

#Arg -> type id | empty
def _parseOneArg(tokens):
    global index
    global scope
    errormsg = 'Error: Expected \')\''
    args = {} #dict = {name: type}
    
    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        typeNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
        index += 1

        errormsg = 'Error: Missing a identifier after type'
        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            typeNode.add_child(ASTNode(tokens[str(index)][cc.TOKEN_INDEX]))
            args[tokens[str(index)][cc.TOKEN_INDEX]] = tokens[str(index-1)][cc.TOKEN_INDEX] #We add the argument to our dict, the negatives are there so we can grab the correct tokens
            index += 1
            return typeNode, args
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == ')': #If we hit the end of args
        return ASTNode(""), args
    
    _customError(errormsg, tokens, index)


#Start of parsing within function ----------------


#Used to parse inside of a functions brackets, will go through local_decls and stmtList
def _parseInFunction(tokens, declNode):
    global index
    global scope

    index += 1
    local_declsNode = _parseLocalDecls(tokens)

    if local_declsNode != None: #local decls can be nothing, so we don't want to add it if it is nothing
        declNode.add_child(local_declsNode)

    stmtListNode = ASTNode("stmtList")
    stmtList = _parseStmtList(tokens, stmtListNode)

    if stmtList != None: #stmts can be nothing
        declNode.add_child(stmtList)

    return declNode

#Start of local_decls parser ----------------

#local_decls -> local_decl local_decls | local_decl
def _parseLocalDecls(tokens, local_declsNode = ASTNode("local_decls")):
    local_declsNodechild = _parseALocalDecl(tokens)

    if local_declsNodechild == None: # we allowed to have no local_decls
        return None
    
    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type' or tokens[str(index)][cc.TOKEN_TYPE_INDEX] == "type modifier": #are there more local_decls?
        local_declsNode2 = _parseLocalDecls(tokens, local_declsNode)
        local_declsNode2.add_child(local_declsNodechild)

    else:
        local_declsNode.add_child(local_declsNodechild)

    return local_declsNode

#local_decl -> TypeModifier type id; | TypeModifier type id = endofDecl; | empty
def _parseALocalDecl(tokens, typeModifier = None):
    global index
    global scope

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type' or re.match(grammar['TypeModifier'][0], tokens[str(index)][cc.TOKEN_INDEX]): #checking to see if our decleration starts with a type or typeModifier
        id_decl = _parsingtheRestofLocalDecl(tokens, typeModifier)
        return id_decl

    elif tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type modifier':
        declModifier = tokens[str(index)][cc.TOKEN_INDEX]
        index += 1
        local_decl = _parseALocalDecl(tokens, declModifier)
        if local_decl == None:
            _customError("Error: Invalid local_decl", tokens, index)
        return local_decl

    return None #We return none in the case that there are no local_decls

#I broke this out into a new function for readability, If we find a type or typeModifier we call this and start to check for typemodifiers and ids
#typemodifier -> signed | unsigned | long | short | empty
def _parsingtheRestofLocalDecl(tokens, typeModifier):
    global index
    global scope
    declType = tokens[str(index)][cc.TOKEN_INDEX]
    local_decl = ASTNode(declType)
    index += 1

    errormsg = 'Error: expected a identifier'


    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type' or re.match(grammar['TypeModifier'][0], tokens[str(index)][cc.TOKEN_INDEX]): #There can be two type modifiers in a row, so we check for that. We want to not do an else, because there could just be the one type modifier or type
        typeModifier = declType#Change the first declType to the typeModifier, since it appeared this second type
        declType = tokens[str(index)][cc.TOKEN_INDEX]
        local_decl = ASTNode(declType)
        index += 1

    if tokens[str(index)][cc.TOKEN_INDEX] == '*':#We want to check for a pointer
        declType += tokens[str(index)][cc.TOKEN_INDEX]
        local_decl = ASTNode(declType)
        index += 1

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
        declId = tokens[str(index)][cc.TOKEN_INDEX]
        id_decl = ASTNode(declId)

        if typeModifier != None:#We are seeing if the type modifier exists, if not we will pass in a empty node
            id_decl.add_child(ASTNode(typeModifier))

        id_decl.add_child(local_decl)
        index += 1

        errormsg = 'Error: Invalid local_decl, expected a \';\''
        if tokens[str(index)][cc.TOKEN_INDEX] == ';':
            symbolTable.add_variable(declId, declType, scope) # we wait to add this till we know it is valid. 
            #Passing in the name of the variable, the type of the variable, and the scope of the variable - Name(id), Type, Scope(Will be function name)
            index += 1
            return id_decl
        
        else: #If there is no semiclon, we check for a '=' and then parse the end of the decl, assuming it is valid
            endOfDecl = _parseEndofDecl(tokens, id_decl, declType, declId) 
            if endOfDecl != None:
                return id_decl
            
    _customError(errormsg, tokens, index) #We only throw this if it is the start of a decl and then is invalid

#endofDecl parser ----------------

#endofDecl -> expr | string | character
def _parseEndofDecl(tokens, local_decl, declType, declId):
    global index
    global scope
    memoryNode = None
    if tokens[str(index)][cc.TOKEN_INDEX] == '=':
        index += 1
        
        if tokens[str(index)][cc.TOKEN_INDEX] == '&':
            memoryNode = ASTNode('&')
            index += 1

        first_number_index = index

        exprNode = _parseExpr(tokens)

        if exprNode != None: #If it isn't none, it is a number/expression that results in a number
            if memoryNode != None:#Is this a memory address using the &?
                memoryNode.add_child(exprNode)
                exprNode = memoryNode

            local_decl = _parseEndofDeclNumber(tokens, local_decl, declType, declId, exprNode, first_number_index) # A lot we are passing in, but I think this is better than creating a list to pass in
            return local_decl
            
        elif tokens[str(index)][cc.TOKEN_INDEX] == '"' or tokens[str(index)][cc.TOKEN_INDEX] == "'":
            local_decl = _parseEndofDeclString(tokens, local_decl, declType, declId)
            return local_decl
                
    _customError("Error: Invalid local_decl", tokens, index)


#We are going through from the first index of the expression and adding them to recreate the expression
def _expressionRecreator(tokens, first_number_index):
    global index
    expression = ''
    while (first_number_index < index):
        if tokens[str(first_number_index)][cc.TOKEN_INDEX] == ')':
            expression = expression[:-1] #We want to remove the last space between the number and the close parens.

        if tokens[str(first_number_index)][cc.TOKEN_TYPE_INDEX] == 'identifier': #Checking to see if the id in the expr is a number

            symbol_type = symbolTable.get_type(tokens[str(first_number_index)][cc.TOKEN_INDEX], scope)
            symbol_global_type = symbolTable.get_type(tokens[str(first_number_index)][cc.TOKEN_INDEX], "global")
            symbol_argument_type = symbolTable.get_args(scope)

            if symbol_type == None:#If the symbol is declared within the local scope, we want to ignore the global declerations
                if symbol_global_type != None:
                    symbol_type = symbol_global_type

                elif tokens[str(first_number_index)][cc.TOKEN_INDEX] in symbol_argument_type:
                    symbol_type = symbol_argument_type[tokens[str(first_number_index)][cc.TOKEN_INDEX]]

            if symbol_type[0] == 'char': #Only non-number type we allow is a char
                _customError('Error: Invalid Expression, cannot use a character in an expression', tokens, first_number_index)

        expression += tokens[str(first_number_index)][cc.TOKEN_INDEX]

        if tokens[str(first_number_index)][cc.TOKEN_INDEX] != '(': #We don't want a space in the case of a open parens
            expression += ' '
        first_number_index += 1

    return expression.strip()

#Parses our number endofDecl
def _parseEndofDeclNumber(tokens, local_decl, declType, declId, exprNode, first_number_index):
    global scope
    global index
    local_decl.add_child(exprNode)

    if re.match(grammar['NumType'][0], declType) or re.match(grammar['TypeModifier'][0], declType): #A typemodifier can be a type in c

        if tokens[str(index)][cc.TOKEN_INDEX] == ';':
            expression = _expressionRecreator(tokens, first_number_index) #We want to pass in the value for our symbol table
            symbolTable.add_variable(declId, declType, scope)
            #Pass in the name, type, and scope
            symbolTable.add_value(declId, expression, scope)
            #Passing in the name, value, and scope
            index += 1
            return local_decl
        else:
            _customError("Error: Invalid local_decl, missing a \';\'", tokens, index)
    else:
        index -= 1 #Go back to number start
        _customError('Error: Invalid assignment, expected ' + declType + ' but received a non-' + declType + ' value', tokens, index)

#Parses our string and character endofDecl
def _parseEndofDeclString(tokens, local_decl, declType, declId):
    global index
    global scope
    index += 1
    second_half_of_decl = tokens[str(index-1)][cc.TOKEN_INDEX]

    if declType == 'char':
        value = tokens[str(index)][cc.TOKEN_INDEX]
        second_half_of_decl += tokens[str(index)][cc.TOKEN_INDEX] + tokens[str(index-1)][cc.TOKEN_INDEX]
        index += 2 #We want to skip the closing quote

        local_decl.add_child(ASTNode(second_half_of_decl))
        if tokens[str(index)][cc.TOKEN_INDEX] == ';':
            symbolTable.add_variable(declId, declType, scope)
            symbolTable.add_value(declId, value, scope)
            #Passing in name, value, and scope for strings/characters we have to push it back further to grab the right tokens
            index += 1
            return local_decl
        else:
            _customError("Error: Invalid local_decl, missing a \';\'", tokens, index)
    else:
        _customError('Error: Invalid assignment, expected ' + declType + ' but received a non-' + declType + ' value', tokens, index)


#stmtList parsing ----------------

#stmtList -> stmt | stmt stmtList
def _parseStmtList(tokens, stmtListNode):
    stmtNode = _parseStmt(tokens)
    if stmtNode == None:
        return None
    
    if tokens[str(index)][cc.TOKEN_INDEX] != '}':
        stmtListNode.add_child(stmtNode)
        stmtListNode2 = _parseStmtList(tokens, stmtListNode)
        return stmtListNode2
    
    else:
        stmtListNode.add_child(stmtNode)

    return stmtListNode

#start of stmt parser ----------------

#stmt -> returnstmt | ifstmt | assignstmt | whilestmt |  functionCall | empty
def _parseStmt(tokens):
    global index

    if tokens[str(index)][cc.TOKEN_INDEX] == 'return':
        returnNode = _parseReturnStmt(tokens)
        return returnNode
        
    elif tokens[str(index)][cc.TOKEN_INDEX] == 'if':
        returnNode = _parseIfStmt(tokens)
        return returnNode
        
    elif tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier' and tokens[str(index+1)][cc.TOKEN_INDEX] == '=':
        returnNode = _parseAssignStmtInitialCheck(tokens)
        return returnNode
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == 'while':
        returnNode = _parseWhileStmt(tokens)
        if returnNode != None:
            return returnNode
        
    elif tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier': #We don't do both checks in the same statement, that way if there is an identifier, we will error. 
        if tokens[str(index + 1)][cc.TOKEN_INDEX] == '(':#We wait to increase the index after the check, so we can leave the error index the same
            index += 2 
            returnNode = _parseFunctionCall(tokens)
            return returnNode
        else: 
            _customError("Error: Invalid statement", tokens, index)
        
    return None

#Function call parser ----------------

#functionCall -> id(Params);
def _parseFunctionCall(tokens):
    global index
    global scope
    errormsg = 'Error: Invalid function call, function isn\'t declared'
    mainNode = ASTNode("functionCall")

    functionName = tokens[str(index-2)][cc.TOKEN_INDEX]

    isFunction = symbolTable.get_scope_type(functionName)

    if isFunction != None:#If the function is declared
        functionNode = ASTNode(functionName)

        paramNode, params = _setupParseParameters(tokens, functionNode)

        if paramNode != None: 
            mainNode.add_child(paramNode)

        functionArguments = symbolTable.get_args(functionName)

        _checkingPassedInTypesWithParameters(tokens, params, functionArguments)
        
        errormsg = 'Error: Invalid function call, missing a \')\''
        if tokens[str(index)][cc.TOKEN_INDEX] == ')':
            index += 1
            errormsg = 'Error: Invalid function call, missing a \';\''
            if tokens[str(index)][cc.TOKEN_INDEX] == ';':
                index += 1
                return mainNode
    
    _customError(errormsg, tokens, index)

#Checking the types that were passed in versus the function argument types
def _checkingPassedInTypesWithParameters(tokens, args, functionArguments):
    global index
    global scope

    errormsg = 'Error: Invalid function call, passed in the wrong type'
    if (args == {} and functionArguments == {}) or (args == None and functionArguments == None) or (args == None and functionArguments == {}) or (args == {} and functionArguments == None): #Just saying that none and {} are equal for these purposes.
        return None
    
    elif len(args) != len(functionArguments):
        errormsg = 'Error: Invalid function call, passed in the wrong amount of arguments'

    else:
        argsValues = list(args.values()) #Turning our dicts into lists, makes it easier to compare values
        functionArgumentsValues = list(functionArguments.values())
        for arg_value, functionArg_value in zip(argsValues, functionArgumentsValues):
            if arg_value != functionArg_value:
                errormsg = 'Error: Invalid function call, passed in type ' + arg_value + ' but expected type ' + functionArg_value
                _customError(errormsg, tokens, index)
        return None
            
#Just like _setupParseArgs, we are creating a node to pass in, then checking to see if there are any params
def _setupParseParameters(tokens, functionNode):
    global index

    paramNode, params = _parseParameters(tokens, functionNode)

    if paramNode == None:
        return functionNode, None
    
    functionNode.add_child(paramNode)
    return functionNode, params

#params -> param, params | param
def _parseParameters(tokens, mainNode):
    global index

    paramNode, params = _parseOneParam(tokens)

    if paramNode == None:
        return None, None
    
    if tokens[str(index)][cc.TOKEN_INDEX] == ',':#Looking to see if there are multiple params |  ',' is our indicator
        mainNode.add_child(paramNode)
        index += 1
        paramNode2, params2 = _parseParameters(tokens, mainNode)
        if params2 == None:
            _customError("Error: Invalid function call, missing a parameter after the ,", tokens, index)

        params.update(params2)
        return paramNode2, params
    
    return paramNode, params
    
#param -> expr | string | character | empty
def _parseOneParam(tokens):
    global index
    global scope
    params = {}

    errormsg = 'Error: Expected \')\' Temp'
    first_number_index = index
    
    exprNode = _parseExpr(tokens)

    if exprNode != None: #A expression can be a ID or a number
        expression = _expressionRecreator(tokens, first_number_index)
        if len(expression) == 1 and tokens[str(first_number_index)][cc.TOKEN_TYPE_INDEX] == 'identifier': #If there is only a variable, our _parseExpr makes sure it is already declared.
            symbol_type = symbolTable.get_type(tokens[str(first_number_index)][cc.TOKEN_INDEX], scope)
            params[expression] = symbol_type[0]
        else: 
            params[expression] = 'int'

        paramNode = ASTNode(expression)
        return paramNode, params
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == '\'' or tokens[str(index)][cc.TOKEN_INDEX] == '\"':
        index += 1
        paramNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
        params[tokens[str(index)][cc.TOKEN_INDEX]] = 'char'
        index += 2 #We want to skip the closing quote
        return paramNode, params
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == ')':
        return None, None
        
    _customError(errormsg, tokens, index)


#return stmt parser ----------------
#returnstmt -> return; | return expr; | return character | return string | return id;
def _parseReturnStmt(tokens):
    global index
    returnNode = ASTNode("return")
    index += 1

    first_number_index = index
    exprNode = _parseExpr(tokens)

    if exprNode != None: #Return can be a id or number.
        returnValue = _parseReturnStmtNumberAndID(tokens, first_number_index) #We don't use the returnValue, but it is because I have already succesfully parsed the expr, I just need to make sure it is a valid return type
        returnNode.add_child(exprNode)
        return returnNode
        
    elif tokens[str(index)][cc.TOKEN_INDEX] == ';': #If we have a return with no value
        index += 1
        return returnNode
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == '\'' or tokens[str(index)][cc.TOKEN_INDEX] == '\"':
        returnValue = _parseReturnStmtChar(tokens)
        returnNode.add_child(returnValue)
        return returnNode

    _customError("Error: Invalid return statement", tokens, index)

#refactored from _parseReturnStmt. We want to check to see if the type of our variable matches the return type of the function
def _parseReturnStmtChar(tokens):
    global index
    scope_type = symbolTable.get_scope_type(scope)
    if scope_type == 'char':
        index += 1
        returnValue = tokens[str(index)][cc.TOKEN_INDEX]
        index += 2 #We want to skip the closing quote
        if tokens[str(index)][cc.TOKEN_INDEX] == ';':
            index += 1
            return ASTNode(returnValue)
        else:
            _customError("Error: Invalid return statement, missing a semicolon", tokens, index)
    else:
        _customError("Error: Invalid return type, expected a return type of " + scope_type + " but received a char type", tokens, index)

#refactored from _parseReturnStmt. We want to check to see if the type of our variable matches the return type of the function
def _parseReturnStmtNumberAndID(tokens, first_number_index):
    global index

    returnValue = _expressionRecreator(tokens, first_number_index)

    if len(returnValue) == 1 and tokens[str(first_number_index)][cc.TOKEN_TYPE_INDEX] == 'identifier':#Is our return a variable?

        idType = symbolTable.get_type(tokens[str(first_number_index)][cc.TOKEN_INDEX], scope)
        globalisType = symbolTable.get_type(tokens[str(first_number_index)][cc.TOKEN_INDEX], "global") #Checking to see if the variable is declared on a global or local scale at least.
        functionArguments = symbolTable.get_args(scope)

        if globalisType != None:
            idType = globalisType

        elif tokens[str(first_number_index)][cc.TOKEN_INDEX] in functionArguments:
            idType = functionArguments[tokens[str(first_number_index)][cc.TOKEN_INDEX]]

        elif idType == None:
            _customError("Error: Undeclared identifier", tokens, index)

    scope_type = symbolTable.get_scope_type(scope)

    #If the type of the scope is a number type and is our expr a number type, or is it a big expr that will result in a number?
    if re.match(grammar['NumType'][0], scope_type) and (len(returnValue) > 1 or tokens[str(first_number_index)][cc.TOKEN_TYPE_INDEX] == 'number'): #A number can fit in with both a float and int
        if tokens[str(index)][cc.TOKEN_INDEX] == ';':
            index += 1
            return returnValue #We don't need ';' in our AST
        
    if scope_type == 'char' and tokens[str(first_number_index)][cc.TOKEN_TYPE_INDEX] == 'number':
        _customError("Error: Invalid return type", tokens, index)
        
    #Does our scope type match the type of our variable, or are both of our types number types?
    elif idType[0] == scope_type or (re.match(grammar['NumType'][0], idType[0]) and re.match(grammar['NumType'][0], scope_type)): #We are seeing if the type of our variable matches the return type of the function
        if tokens[str(index)][cc.TOKEN_INDEX] == ';':
            index += 1
            return returnValue
        
    _customError("Error: Invalid return type", tokens, index-1)

#while stmt parser ----------------

# whilestmt -> while (conditional_expr) {stmtList}
def _parseWhileStmt(tokens):
    global index
    global scope
    index += 1
    errormsg = 'Error: Invalid while statement'

    if tokens[str(index)][cc.TOKEN_INDEX] == '(':
        index += 1
        whileNode = _setParseConditionalExpr(tokens, ASTNode('while'))
        return whileNode

    _customError(errormsg, tokens, index)

#If stmt parser ----------------

#Starts parsing our if stmt, will check for the open parens and then an else stmt
#ifstmt -> if (if_expr) {stmtList} | if (if_expr) {stmtList} else {stmtList}
def _parseIfStmt(tokens):
    global index
    
    index += 1

    if tokens[str(index)][cc.TOKEN_INDEX] == '(':
        index += 1
        if_exprNode = _setParseConditionalExpr(tokens, ASTNode('if')) #Passes it to another part that starts parsing the if_expr
        if if_exprNode == None:
            _customError("Error: Invalid if statement", tokens, index)

        elif tokens[str(index)][cc.TOKEN_INDEX] == 'else':#Checking to see if this is an if else stmt
            else_exprNode = _paseElseStmt(tokens)
            if_exprNode.add_child(else_exprNode)
            return if_exprNode
            

    _customError("Error: Invalid if statement", tokens, index)
    return None

#We use this with both the while and if statements
#conditonal_exprs -> conditional_expr && conditional_expr | conditional_expr || conditional_expr | conditional_expr
def _setParseConditionalExpr(tokens, initalNode):
    ParenNode = ASTNode("()")

    conditional_expr = _parseMultipleConditonalExprs(tokens, ParenNode)

    initalNode.add_child(conditional_expr)

    initalNode = _parseStmtInBrackets(tokens, initalNode)

    return initalNode

#Used to parse the multiple conditional exprs within the parenns of an if or while statement
#conditional_exprs -> conditional_expr && conditional_expr | conditional_expr || conditional_expr | conditional_expr
def _parseMultipleConditonalExprs(tokens, keywordNode):
    global index
    global scope
    
    relOpNode = _parseConditionalExpr(tokens)

    if tokens[str(index)][cc.TOKEN_INDEX] == '&&' or tokens[str(index)][cc.TOKEN_INDEX] == '||': #Checking to see if there are multiple conditional exprs
        logicOP = tokens[str(index)][cc.TOKEN_INDEX]
        logicOPNode = ASTNode(logicOP)
        logicOPNode.add_child(relOpNode)

        index += 1

        logicOPNode = _parseMultipleConditonalExprs(tokens, logicOPNode)
        keywordNode.add_child(logicOPNode)

        return keywordNode
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == ')':
        index += 1
        keywordNode.add_child(relOpNode)
        return keywordNode
    
    _customError("Error: Invalid conditional", tokens, index)
                        
#Used to parsse the conditional expr inside statements
#ifstmt -> if (conditional_expr) {stmtList}
#whilestmt -> while (conditional_expr) {stmtList}
#conditional_expr -> expr relop expr
def _parseConditionalExpr(tokens):
    global index
    global scope
    errormsg = 'Error: Invalid Conditional, incorrect syntax'

    expr = _parseExpr(tokens)

    if expr != None:
        if re.match(grammar['Relop'][0], tokens[str(index)][cc.TOKEN_INDEX]):
            relOp = tokens[str(index)][cc.TOKEN_INDEX]
            index += 1
            second_expr = _parseExpr(tokens)

            errormsg = 'Error: Invalid if statement, expected a variable or number after the relop'

            if second_expr != None:
                errormsg = 'Error: Invalid if statement, expected a \')\''

                relOpNode = ASTNode(relOp)
                relOpNode.add_child(expr)
                relOpNode.add_child(second_expr)
                return relOpNode

    
    _customError(errormsg, tokens, index)

#Used to parse the stmts within the brackets of an if stmt
#ifstmt -> if (if_expr) {stmtList}
#whilestmt -> while (conditional_expr) {stmtList}
def _parseStmtInBrackets(tokens, stmtNode):
    global index
    global scope

    errormsg = 'Error: Invalid statement, expected a \'{\''
    
    if tokens[str(index)][cc.TOKEN_INDEX] == '{':
        index += 1
        stmtList = _parseStmtList(tokens, ASTNode("stmtList")) #Only allowing stmts for now

        if tokens[str(index)][cc.TOKEN_INDEX] == '}':
            index += 1
            bracketNode = ASTNode('{ }')

            if stmtList != None:# We can have no stmts within the else.
                bracketNode.add_child(stmtList)

            stmtNode.add_child(bracketNode)
            return stmtNode
            
    else:#Just to move the pointer back to the previous token so the error message looks neater
        index -= 1

    _customError(errormsg, tokens, index)

# if (if_expr) {stmtList} else {stmtList}
def _paseElseStmt(tokens):

    global index
    errorstmt = 'Error: Missing a \'{\' in else stmt'#Generating better help messages for the user
    index += 1

    if tokens[str(index)][cc.TOKEN_INDEX] == '{':
        index += 1
        stmtList = _parseStmtList(tokens, ASTNode("stmtList"))

        errorstmt = 'Error: Missing a \'}\' in else stmt' #Generating better help messages for the user

        if tokens[str(index)][cc.TOKEN_INDEX] == '}':
            index += 1
            else_exprNode = ASTNode("else")
            if stmtList != None:#An else stmt can have nothing within it, so we don't want to add a child if it is empty
                bracketNode = ASTNode('{ }')
                bracketNode.add_child(stmtList)
                else_exprNode.add_child(bracketNode)

            return else_exprNode
        
    _customError(errorstmt, tokens, index) #we only hit this if there is an error


#assignment stmt parser ----------------

#Checking to see if the variable is declared somewhere within our program.
def _parseAssignStmtInitialCheck(tokens):
    iftype = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], scope)
    globalisType = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], "global") #Checking to see if the variable is declared on a global or local scale at least.
    functionArguments = symbolTable.get_args(scope)

    if tokens[str(index)][cc.TOKEN_INDEX] in functionArguments: #Checking to see if the variable is a function argument
        returnNode = _parseAssignStmt(tokens, functionArguments[tokens[str(index)][cc.TOKEN_INDEX]])
        return returnNode
    
    elif iftype != None: #if it is not a global, pass in the function scope
        returnNode = _parseAssignStmt(tokens, iftype[0])
        return returnNode
        
    elif globalisType != None:
        returnNode = _parseAssignStmt(tokens, globalisType[0])
        return returnNode
    else:
        _customError("Error: Undeclared identifier", tokens, index)



#assignstmt -> id = endofDecl;
def _parseAssignStmt(tokens, idType):
    global index
    assignID = tokens[str(index)][cc.TOKEN_INDEX]
    index += 1
    errormsg = 'Error: Invalid assignment'

    if tokens[str(index)][cc.TOKEN_INDEX] == '=':
        exprNode = _parseEndofDecl(tokens, ASTNode(assignID), idType, assignID)
        return exprNode
            
    _customError(errormsg, tokens, index)


#Expr parser ----------------

def _parseExpr(tokens):
    global index
    termNode = _parseTerm(tokens)

    if termNode == None:#We aren't throwing errors for these because at the parse_end0fDecl we use it to determine if it a number or not. I will pass in a ' if it isn't.
        return None
    
    if len(tokens) > index and tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'addOP':
        addOpNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
        addOpNode.add_child(termNode)
        index+= 1
        exprNode = _parseExpr(tokens)

        if exprNode == None:
            return None
        
        addOpNode.add_child(exprNode)
        return addOpNode
    
    return termNode

def _parseTerm(tokens):
    global index
    factorNode = _parseFactor(tokens)

    if factorNode == None:
        return None

    if len(tokens) > index and tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'mulOP':
        mulOpNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
        mulOpNode.add_child(factorNode)
        index += 1
        termNode = _parseTerm(tokens)

        if termNode == None:
            return None
        
        mulOpNode.add_child(termNode)
        return mulOpNode
    
    return factorNode

def _parseFactor(tokens):
    global index
    global scope

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
        #Is our Identifier declared in a global, local, or parameter scope?
        isIdInFunction = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], scope)
        isIdInGlobal = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], "global")
        isIdInFunctionParams = symbolTable.get_args(scope)

        if isIdInFunction != None or isIdInGlobal != None:
            factor = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
            index += 1
            return factor
        elif tokens[str(index)][cc.TOKEN_INDEX] in isIdInFunctionParams:
            factor = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
            index += 1
            return factor
        else:
            _customError("Error: Undeclared identifier", tokens, index)
    
    elif tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'number': 
        factor = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
        index += 1
        return factor
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == '(':
        factor = tokens[str(index)][cc.TOKEN_INDEX]
        index += 1
        exprNode = _parseExpr(tokens)

        if exprNode == None:
            return None
        
        if tokens[str(index)][cc.TOKEN_INDEX] == ')':
            factor += tokens[str(index)][cc.TOKEN_INDEX]
            parenNode = ASTNode(factor)
            parenNode.add_child(exprNode)
            index += 1
            return parenNode
        
    else:
        return None