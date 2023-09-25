'''
-@author: Tyler Ray
-@date: 9/24/2023

- Will parse through our token list and output a AST along with a symbol table
- Works for the below grammar
- ***WORK IN PROGRESS***
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
    'Arg': ['Type id', ''],

    'Local_Decls': ['Local_Decl', 'Local_Decl Local_Decls'],
    'Local_Decl': ['Type id;', 'Type id = EndOfDecl;',''], # we aren't going to check and see if the EndOfDecl is valid, we will just assume it is. TODO: check if it is valid

    'StmtList': ['Stmt', 'Stmt StmtList'],
    'Stmt': ['ReturnStmt', 'AssignStmt', 'WhileStmt', 'IfStmt', ''],

    'ReturnStmt': ['return num;', 'return id;', 'return;', 'return expr;', 'return character', 'return string'],
    'AssignStmt': ['id = EndOfDecl;'],
    'WhileStmt': ['while (Conditional_Expr) \{StmtList\}'],
    'IfStmt': ['if (Conditional_Expr) \{StmtList\}', 'if (Conditional_Expr) \{StmtList\} else \{StmtList\}'],

    'Conditional_Expr': ['expr Relop expr'],
    'Relop': [r'^==$|^!=$|^>$|^>=$|^<$|^<=$'],

    'EndOfDecl': ['Expr', 'string', 'character'],

    'Expr': ['Term + Expr', 'Term - Expr', 'Term'],
    'Term': ['Factor * Term', 'Factor / Term', 'Factor'],
    'Factor': ['num', '(Expr)', 'id'],

    'Type': ['int', 'void', 'float', 'char'],

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
    
    def ast_to_expr(self):
        if self.value == "+":
            return f"({self.children[0].ast_to_expr()} + {self.children[1].ast_to_expr()})"
        elif self.value == "*":
            return f"({self.children[0].ast_to_expr()} * {self.children[1].ast_to_expr()})"
        else:
            return str(self.value)


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
    
    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type': #are there more local_decls?
        local_declsNode2 = _parseLocalDecls(tokens, local_declsNode)
        local_declsNode2.add_child(local_declsNodechild)
    else:
        local_declsNode.add_child(local_declsNodechild)

    return local_declsNode

#local_decl -> type id; | type id = endofDecl; | empty
def _parseALocalDecl(tokens):
    global index
    global scope
    errormsg = 'Error: Invalid local_decl'

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        declType = tokens[str(index)][cc.TOKEN_INDEX]
        local_decl = ASTNode(declType)
        index += 1

        errormsg += ', expected a identifier'
        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            declId = tokens[str(index)][cc.TOKEN_INDEX]
            id_decl = ASTNode(declId)
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

    return None #We return none in the case that there are no local_decls


#endofDecl parser ----------------

#endofDecl -> expr | string | character
def _parseEndofDecl(tokens, local_decl, declType, declId):
    global index
    global scope
    
    if tokens[str(index)][cc.TOKEN_INDEX] == '=':
        index += 1
        exprNode = _parseExpr(tokens)

        if exprNode != None: #If it isn't none, it is a number/expression that results in a number
            local_decl = _parseEndofDeclNumber(tokens, local_decl, declType, declId, exprNode)
            return local_decl
            
        elif tokens[str(index)][cc.TOKEN_INDEX] == '"' or tokens[str(index)][cc.TOKEN_INDEX] == "'":
            local_decl = _parseEndofDeclString(tokens, local_decl, declType, declId)
            return local_decl
                
    _customError("Error: Invalid local_decl", tokens, index)



#Parses our number endofDecl
def _parseEndofDeclNumber(tokens, local_decl, declType, declId, exprNode):
    global scope
    global index
    local_decl.add_child(exprNode)

    if (declType == 'int' or declType == 'float') and tokens[str(index-1)][cc.TOKEN_TYPE_INDEX] == 'number':

        if tokens[str(index)][cc.TOKEN_INDEX] == ';':
            symbolTable.add_variable(declId, declType, scope)
            #Pass in the name, type, and scope
            symbolTable.add_value(declId, exprNode.ast_to_expr(), scope)
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

#stmt -> returnstmt | ifstmt | assignstmt | whilestmt | empty
def _parseStmt(tokens):
    global index
    if tokens[str(index)][cc.TOKEN_INDEX] == 'return':
        returnNode = _parseReturnStmt(tokens)
        return returnNode
        
    elif tokens[str(index)][cc.TOKEN_INDEX] == 'if':
        returnNode = _parseIfStmt(tokens)
        return returnNode
        
    elif tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
        iftype = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], scope)
        globalisType = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], "global") #Checking to see if the variable is declared on a global or local scale at least.
        functionArguments = symbolTable.get_args(scope)

        if tokens[str(index)][cc.TOKEN_INDEX] in functionArguments: #Checking to see if the variable is a function argument
            returnNode = _parseAssignStmt(tokens, functionArguments[tokens[str(index)][cc.TOKEN_INDEX]])
            return returnNode
        elif iftype != None:#if it is not a global, pass in the function scope
            returnNode = _parseAssignStmt(tokens, iftype[0])
            return returnNode
            
        elif globalisType != None:
            returnNode = _parseAssignStmt(tokens, globalisType[0])
            return returnNode
        else:
            _customError("Error: Undeclared identifier", tokens, index)
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == 'while':
        returnNode = _parseWhileStmt(tokens)
        if returnNode != None:
            return returnNode
        
    return None

#return stmt parser ----------------

#returnstmt -> return; | return expr; | return character | return string | return id;
def _parseReturnStmt(tokens):
    global index
    returnNode = ASTNode("return")
    index += 1

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'number' or tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier': #Return can be a id or number.
        
        numNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])

        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':#Is our return a variable?
            idType = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], scope)

        returnNode.add_child(numNode)
        index += 1

        scope_type = symbolTable.get_scope_type(scope)
        if (scope_type == 'int' or scope_type == 'float') and tokens[str(index-1)][cc.TOKEN_TYPE_INDEX] == 'number': #A number can fit in with both a float and int
            if tokens[str(index)][cc.TOKEN_INDEX] == ';':
                index += 1
                return returnNode #We don't need ';' in our AST
        elif idType[0] == scope_type: #We are seeing if the type of our variable matches the return type of the function
            if tokens[str(index)][cc.TOKEN_INDEX] == ';':
                index += 1
                return returnNode
            
        _customError("Error: Invalid return type", tokens, index-1)

    elif tokens[str(index)][cc.TOKEN_INDEX] == ';': #If we have a return with no value
        index += 1
        return returnNode
    
    _customError("Error: Invalid return statement", tokens, index)


#while stmt parser ----------------

# whilestmt -> while (conditional_expr) {stmtList}
def _parseWhileStmt(tokens):
    global index
    global scope
    whileNode = ASTNode("while")
    index += 1
    errormsg = 'Error: Invalid while statement'

    if tokens[str(index)][cc.TOKEN_INDEX] == '(':
        index += 1
        exprNode = _parseExpr(tokens)
        errormsg = 'Error: Invalid while statement, There must be something within the parens'
        if exprNode != None:
            conditionalExprNode = _parseConditionalExpr(tokens, exprNode)
            whileNode.add_child(conditionalExprNode)
            whileNode = _parseStmtInBrackets(tokens, whileNode)
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
        if_exprNode = _parse_if_expr(tokens) #Passes it to another part that starts parsing the if_expr
        if if_exprNode == None:
            _customError("Error: Invalid if statement", tokens, index)

        elif tokens[str(index)][cc.TOKEN_INDEX] == 'else':#Checking to see if this is an if else stmt
            else_exprNode = _paseElseStmt(tokens)
            if_exprNode.add_child(else_exprNode)
            return if_exprNode
            

    _customError("Error: Invalid if statement", tokens, index)
    return None

#if_expr -> expr relop expr
#ifstmt -> if (if_expr) {stmtList}
def _parse_if_expr(tokens):
    global index
    errormsg = 'Error: Invalid if statement'
    expr = _parseExpr(tokens)

    if expr != None:
        if re.match(grammar['Relop'][0], tokens[str(index)][cc.TOKEN_INDEX]):
            if_expr = ASTNode('if')
            bracketNode = _parseConditionalExpr(tokens, expr)
            if_expr.add_child(bracketNode)
            if_expr = _parseStmtInBrackets(tokens, if_expr)
            return if_expr
                            
        else: #Only if it is just a number
            return expr
    
    _customError(errormsg, tokens, index)

#Used to parse the if expr within the parens of an if stmt
#ifstmt -> if (conditional_expr) {stmtList}
#whilestmt -> while (conditional_expr) {stmtList}
def _parseConditionalExpr(tokens, expr):
    global index
    global scope

    relOp = tokens[str(index)][cc.TOKEN_INDEX]
    index += 1
    second_expr = _parseExpr(tokens)

    errormsg = 'Error: Invalid if statement, expected a variable or number after the relop'

    if second_expr != None:
        errormsg = 'Error: Invalid if statement, expected a \')\''

        if tokens[str(index)][cc.TOKEN_INDEX] == ')':
            index += 1

            bracket_Node = ASTNode('( )') #We want to add our bracket node to our if_expr, then within it show the expression
            bracket_Node.add_child(expr)
            bracket_Node.add_child(ASTNode(relOp))
            bracket_Node.add_child(second_expr)
            return bracket_Node

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
        isIdInFunction = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], scope)
        isIdInGlobal = symbolTable.get_type(tokens[str(index)][cc.TOKEN_INDEX], "global")
        isIdInFunctionValue = symbolTable.get_args(scope)

        if isIdInFunction != None or isIdInGlobal != None:
            factor = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
            index += 1
            return factor
        elif tokens[str(index)][cc.TOKEN_INDEX] in isIdInFunctionValue:
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

