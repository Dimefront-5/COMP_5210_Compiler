'''
-@author: Tyler Ray
-@date: 9/23/2023

- Will parse through our token list and output a AST along with a symbol table
- Works for the below grammar
- ***WORK IN PROGRESS***
'''
import CompilerConstants as cc
from anytree import RenderTree #Our fancy printing with AST
import re
import sys

'''
Need to change grammar to:
Expr -> Term + Expr, Term - Expr, Term
Term -> Factor * Term, Factor / Term, Factor
Factor -> num, (Expr), id
'''
#TODO: Rewrite grammar as I add more things
#grammar for our parser
grammar = {
    'Program': ['declList'],
    'declList': ['decl', 'decl declList'],
    'decl': ['type id (Args) \{local_decls stmtList\}'],
    'type': ['int', 'void', 'float', 'char'],
    'Args': ['Arg', 'Arg, Args'],
    'Arg': ['type id', ''],
    'stmtList': ['stmt', 'stmt stmtList'],
    'stmt': ['returnstmt', ''],
    'ifstmt': ['if (if_expr) \{stmtList\}', 'if (if_expr) \{stmtList\} else \{stmtList\}'],
    'if_expr': ['expr relop expr'], #I know you can have an if with just a number, but for now I am not allowing it
    'relop': [r'^==$|^!=$|^>$|^>=$|^<$|^<=$'],
    'returnstmt': ['return num;', 'return id;', 'return;', 'return expr;', 'return character'],
    'local_decls': ['local_decl', 'local_decl local_decls'],
    'local_decl': ['type id;', 'type id = endofDecl;',''], # we aren't going to check and see if the endofDecl is valid, we will just assume it is. TODO: check if it is valid
    'endofDecl': ['num', 'id', 'string', 'character'],#Need to put expressions in this
    #------Previous grammar is below. New Grammar is above
    'Expr': ['Expr + Term', 'Expr - Term', 'Term'],
    'Term': ['Term * Factor', 'Term / Factor', 'Factor'],
    'Factor': ['num', '(Expr)', 'id'],
    'string': [r'^"[^"]*"$'],
    'character': ['\'[a-zA-Z]\''],
    'num': [r'^[\d]+$ | ^[\d]+\.[\d]+$'],
    'id': [r'^[A-Za-z_][\w_]*$'] 
}

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

    def add_scope(self, name, fun_type, params):
        if name not in self.symbolTable:
            self.symbolTable[name] = {}  # Create a new scope
        self.symbolTable[name]['return_type'] = fun_type
        self.symbolTable[name]['args'] = params

    def add_value(self, name, value, scope):
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


#Will take a list of tokens and the index of the token that caused the error and return a string with the error message pointing to the issue
#I had github copilot generate this for me.
def Customerror(message, tokens, index):
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


global index
index = 0
global symbolTable
symbolTable = SymbolTable()
global scope
scope = "global"

#main function for the parser
def parser(tokens):
    parseTree = _parse_program(tokens)
    return parseTree, symbolTable
    '''
    Keeping this for now, probably will not need it later
    parseTree = ASTNode("Expr") #Start with an expr node

    indexofFirstToken = 0
    parseTree = _parseExpr(tokens, str(indexofFirstToken), parseTree)

    if parseTree == None:
        return None

    isASTValid = _parseValidation(tokens, parseTree)

    if isASTValid == True:
        return parseTree
    else:
        return None
    '''


#----- Inward facing modules

#Function will find every leaf node, if the number of leaf nodes is equal to the number of tokens it is valid syntax. Not needed anymore
def _parseValidation(tokens, parsetree):
    tokensLength = len(tokens)
    count = 0
    numberOfLeafNodes = _findLeafNodes(parsetree, count)

    if numberOfLeafNodes != tokensLength:
        return False
    
    return True

#Finds every leaf node, we won't need this anymore since every token won't be a leaf node now. Will keep for now
def _findLeafNodes(node, count):
    
    if len(node.children) == 0:
        count += 1
        return count

    else:
        for child in node.children:
            count = _findLeafNodes(child, count)

    return count

#program -> declList
def _parse_program(tokens):
    programNode = ASTNode("Program")
    global index

    while index < len(tokens):
        programNode.add_child(_parse_declList(tokens))
        index+=1

    return programNode

#declList -> decl declList | decl
def _parse_declList(tokens, declListNode = ASTNode("declList")):
    global scope

    declNode = _parse_decl(tokens)

    if declNode == None:
        return None
    
    scope = "global"
    if index < len(tokens) and tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        declListNode2 = _parse_declList(tokens, declListNode)
        declListNode2.add_child(declNode)
        return declListNode2
    
    else:
        declListNode.add_child(declNode)
    

    return declListNode


#decl -> type id (Args) {local_decls stmtList}
def _parse_decl(tokens):
    declNode = ASTNode("decl")
    global index
    global scope

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        typeNode = ASTNode("type")
        typeNode.add_child(ASTNode(tokens[str(index)][cc.TOKEN_INDEX]))
        declNode.add_child(typeNode)

        scope_type = tokens[str(index)][cc.TOKEN_INDEX]
        index += 1
        
        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            idNode = ASTNode("id")
            idNode.add_child(ASTNode(tokens[str(index)][cc.TOKEN_INDEX]))
            declNode.add_child(idNode)

            scope = tokens[str(index)][cc.TOKEN_INDEX]
            index += 1
            if tokens[str(index)][cc.TOKEN_INDEX] == '(':
                declNode, args = _setup_parse_args(tokens, declNode)
                symbolTable.add_scope(scope, scope_type, args)

                if tokens[str(index)][cc.TOKEN_INDEX] == ')':
                    index += 1
                    if tokens[str(index)][cc.TOKEN_INDEX] == '{':
                        declNode = _parsing_inside_function(tokens, declNode)
                        if tokens[str(index)][cc.TOKEN_INDEX] == '}':
                            index += 1
                            return declNode
                        
    return None

def _parsing_inside_function(tokens, declNode):
    global index

    index += 1
    local_declsNode = _parse_local_decls(tokens)
    if local_declsNode != None:
        declNode.add_child(local_declsNode)

    stmtListNode = ASTNode("stmtList")
    stmtList = _parse_stmtList(tokens, stmtListNode)

    if stmtList != None:
        declNode.add_child(stmtList)

    return declNode


def _setup_parse_args(tokens, declNode):
    global index

    index += 1
    argsNode = ASTNode("Args")
    
    argsNode, args = (_parse_Args(tokens, argsNode))

    if argsNode != None: #don't add args if there are no args
        declNode.add_child(argsNode)

    return declNode, args

#Args -> Arg, Args | Arg
def _parse_Args(tokens, argsNode):
    global index

    argNode1, initialArgs = _parse_Arg(tokens)

    if tokens[str(index)][cc.TOKEN_INDEX] == ',':#Looking to see if there are multiple args ',' is our indicator
        index += 1
        argNode2, args = _parse_Args(tokens, argsNode)

        initialArgs.update(args) #We want to gather all of the args to add to the function scope, we pass them back so we can add all at once
        argNode2.add_child(argNode1)

        return argNode2, initialArgs
    else: #if no more args
        argsNode.add_child(argNode1)
        return argsNode, initialArgs

#Arg -> type id | empty
def _parse_Arg(tokens):
    global index
    global scope
    args = {} #dict = {name: type}
    
    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        typeNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
        index += 1

        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            typeNode.add_child(ASTNode(tokens[str(index)][cc.TOKEN_INDEX]))
            args[tokens[str(index)][cc.TOKEN_INDEX]] = tokens[str(index-1)][cc.TOKEN_INDEX] #We add the argument to our dict, the negatives are there so we can grab the correct tokens
            index += 1
            return typeNode, args
    
    elif tokens[str(index)][cc.TOKEN_INDEX] == ')': #If we hit the end of args
        return ASTNode(""), args
    
    return None

#local_decls -> local_decl local_decls | local_decl
def _parse_local_decls(tokens, local_declsNode = ASTNode("local_decls")):
    local_declsNodechild = _parse_local_decl(tokens)

    if local_declsNodechild == None: # we allowed to have no local_decls
        return None
    
    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        local_declsNode2 = _parse_local_decls(tokens, local_declsNode)
        local_declsNode2.add_child(local_declsNodechild)
    else:
        local_declsNode.add_child(local_declsNodechild)

    return local_declsNode

#local_decl -> type id; | type id = endofDecl; | empty
def _parse_local_decl(tokens):
    global index
    global scope
    local_decl = ''
    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        local_decl = tokens[str(index)][cc.TOKEN_INDEX]
        index += 1

        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            local_decl += ' ' + tokens[str(index)][cc.TOKEN_INDEX]
            index += 1
            
            if tokens[str(index)][cc.TOKEN_INDEX] == ';':
                symbolTable.add_variable(tokens[str(index-1)][cc.TOKEN_INDEX], tokens[str(index-2)][cc.TOKEN_INDEX], scope) # we wait to add this till we know it is valid. 
                #Passing in the name of the variable, the type of the variable, and the scope of the variable - Name(id), Type, Scope(Will be function name)
                index += 1
                return local_decl
            else:
                endOfDecl = _parse_endofDecl(tokens)
                if endOfDecl != None:
                    local_decl += endOfDecl
                    local_decl = ASTNode(local_decl)
                    return local_decl
                
    
    return None

#TODO: Refactor
#endofDecl -> num | id | string | character
def _parse_endofDecl(tokens):
    global index
    global scope
    second_half_of_decl = ''
    if tokens[str(index)][cc.TOKEN_INDEX] == '=':
        second_half_of_decl += ' ='
        index += 1
        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'number' or tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            second_half_of_decl += ' ' + tokens[str(index)][cc.TOKEN_INDEX]
            index += 1
            if tokens[str(index)][cc.TOKEN_INDEX] == ';':
                symbolTable.add_variable(tokens[str(index-3)][cc.TOKEN_INDEX], tokens[str(index-4)][cc.TOKEN_INDEX], scope)
                symbolTable.add_value(tokens[str(index-3)][cc.TOKEN_INDEX], tokens[str(index-1)][cc.TOKEN_INDEX], scope)
                #Passing in the name, value, and scope
                index += 1
                return second_half_of_decl
            
        elif tokens[str(index)][cc.TOKEN_INDEX] == '"' or tokens[str(index)][cc.TOKEN_INDEX] == "'":
            index += 1
            second_half_of_decl += ' ' + tokens[str(index-1)][cc.TOKEN_INDEX]
            if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'string' or tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'characters':
                second_half_of_decl += tokens[str(index)][cc.TOKEN_INDEX] + tokens[str(index-1)][cc.TOKEN_INDEX]
                index += 2 #We want to skip the closing quote

                if tokens[str(index)][cc.TOKEN_INDEX] == ';':
                    symbolTable.add_variable(tokens[str(index-5)][cc.TOKEN_INDEX], tokens[str(index-6)][cc.TOKEN_INDEX], scope)
                    symbolTable.add_value(tokens[str(index-5)][cc.TOKEN_INDEX], tokens[str(index-2)][cc.TOKEN_INDEX], scope)
                    #Passing in name, value, and scope for strings/characters we have to push it back further to grab the right tokens
                    index += 1
                    return second_half_of_decl
            
    Customerror("Error: Invalid local_decl", tokens, index)
    return None

#stmtList -> stmt | stmt stmtList
def _parse_stmtList(tokens, stmtListNode):
    stmtNode = _parse_stmt(tokens)
    if stmtNode == None:
        return None
    if tokens[str(index)][cc.TOKEN_INDEX] != '}':
        stmtListNode.add_child(stmtNode)
        stmtListNode2 = _parse_stmtList(tokens, stmtListNode)
        return stmtListNode2
    else:
        stmtListNode.add_child(stmtNode)

    return stmtListNode

#stmt -> return num; | if (if_expr) {stmtList} | empty
def _parse_stmt(tokens):
    global index
    if tokens[str(index)][cc.TOKEN_INDEX] == 'return':
        returnNode = _parse_returnstmt(tokens)
        if returnNode != None:
            return returnNode
        
    elif tokens[str(index)][cc.TOKEN_INDEX] == 'if':
        returnNode = _parse_ifstmt(tokens)
        if returnNode != None:
            return returnNode
        
    return None


def _parse_returnstmt(tokens):
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
            
        Customerror("Error: Invalid return type", tokens, index-1)
    else:
        Customerror("Error: Invalid return statement", tokens, index)

#ifstmt -> if (if_expr) {stmtList} | if (if_expr) {stmtList} else {stmtList}
def _parse_ifstmt(tokens):
    global index
    
    index += 1

    if tokens[str(index)][cc.TOKEN_INDEX] == '(':
        index += 1
        if_exprNode = _parse_if_expr(tokens)
        if if_exprNode == None:
            Customerror("Error: Invalid if statement", tokens, index)

        elif tokens[str(index)][cc.TOKEN_INDEX] == 'else':#Checking to see if this is an if else stmt
            else_exprNode = _parse_else(tokens)
            if_exprNode.add_child(else_exprNode)
            return if_exprNode
            

    Customerror("Error: Invalid if statement", tokens, index)
    return None

# if (if_expr) {stmtList} else {stmtList}
def _parse_else(tokens):

    global index
    errorstmt = 'Error: Missing a \'{\' in else stmt'#Generating better help messages for the user
    index += 1

    if tokens[str(index)][cc.TOKEN_INDEX] == '{':
        index += 1
        stmtList = _parse_stmtList(tokens, ASTNode("stmtList"))

        errorstmt = 'Error: Missing a \'}\' in else stmt' #Generating better help messages for the user

        if tokens[str(index)][cc.TOKEN_INDEX] == '}':
            index += 1
            else_exprNode = ASTNode("else")
            if stmtList != None:#An else stmt can have nothing within it, so we don't want to add a child if it is empty
                else_exprNode.add_child(stmtList)

            return else_exprNode
        
    Customerror(errorstmt, tokens, index) #we only hit this if there is an error

#TODO: Refactor, add else stmtList
#if_expr -> expr relop expr
#ifstmt -> if (if_expr) {stmtList}
def _parse_if_expr(tokens):
    global index
    
    expr = _parseExpr(tokens, str(index), ASTNode("Expr"))
    exprString = _combineLeafNodes(expr) #Since we are now using an AST instead of a full parse tree, I need to cut down the parse tree that expr did create. I do this by combining all of the leaf nodes into a string
    print(exprString)                   #In the future I will probably refactor expr to return a string instead of a node, but for now this works
    index +=1

    if exprString != None:
        if re.match(grammar['relop'][0], tokens[str(index)][cc.TOKEN_INDEX]):
            relOp = tokens[str(index)][cc.TOKEN_INDEX]
            index += 1
            second_expr = _parseExpr(tokens, str(index), ASTNode("Expr"))
            second_exprString = _combineLeafNodes(second_expr)
            index += 1

            if second_exprString != None:
                if tokens[str(index)][cc.TOKEN_INDEX] == ')':
                    index += 1
                    if_expr = 'if (' + exprString + relOp + second_exprString + ')' #Creating our if_expr string. I don't want to create individual nodes for each token

                    if tokens[str(index)][cc.TOKEN_INDEX] == '{':
                        index += 1
                        stmtList = _parse_stmtList(tokens, ASTNode("stmtList")) #Only allowing stmts for now

                        if stmtList != None:

                            if tokens[str(index)][cc.TOKEN_INDEX] == '}':
                                index += 1
                                if_exprNode = ASTNode(if_expr)
                                if_exprNode.add_child(stmtList)
                                return if_exprNode
        return expr
    

#These are created to help combine a parse tree into a string
def _combineLeafNodesToString(node, result):
    if len(node.children) == 0:
        result.append(node.value)
    else:
        for child in node.children:
            _combineLeafNodesToString(child, result)

def _combineLeafNodes(node):
    result = []
    _combineLeafNodesToString(node, result)
    return ''.join(result)






#TODO: Fix up, currently does not allow for expr within an if. Probably doesn't allow for expr within a return either, maybe no where.
#Expr parser ----------------

#Parses expr with addOPs, will first parse through the expr before the addOP, we will add that node and a new node for our addOP to our parsetree, then parse through the term after the addOP
def _parseaddOP(tokens, indexOfCurrentToken, recentNode, addOP, indexOfAddop, keyIndexAfterAddOP):
    distanceToTokenAfterOp = 1
    exprNode = ASTNode("Expr")

    listOfTokens = list(tokens.items())
    beforeAddOP = listOfTokens[:indexOfAddop] #We want to cut out the addOP token from the tokens we pass to the expr parser
    afterAddOP = listOfTokens[indexOfAddop+distanceToTokenAfterOp:] #We want to cut out the addOP token from the tokens we pass to the expr parser

    beforeAddOPTokens = dict(beforeAddOP)
    afterAddOPTokens = dict(afterAddOP)

    exprNode = _parseExpr(beforeAddOPTokens, str(indexOfCurrentToken), exprNode)

    if exprNode == None: #if it isn't a valid expr
        return None
    
    recentNode.add_child(exprNode)
    recentNode.add_child(ASTNode(addOP))


    termNode = ASTNode("Term")
    termNode = _parseTerm(afterAddOPTokens, str(int(keyIndexAfterAddOP)+distanceToTokenAfterOp), termNode) #Same as the term parser, we use a keyIndex here because we can't just use i + 1, we need to use the keyIndex of the token after the addOP.
    
    if termNode == None: #if it isn't a valid term
        return None
    
    recentNode.add_child(termNode)

    return recentNode

#Parses through exprs, and depending on if there is a addOP call the addOP parser or the term parser
def _parseExpr(tokens, indexOfCurrentToken, recentNode):
    addOP, indexOfLastAddOP, keyIndexOfTokenAfterOp = index_finder(tokens, "addOP")

    if addOP != '':
        recentNode = _parseaddOP(tokens, indexOfCurrentToken, recentNode, addOP, indexOfLastAddOP, keyIndexOfTokenAfterOp)
        if recentNode == None:
            return None

    else:
        termNode = ASTNode("Term")
        termNode = _parseTerm(tokens, str(indexOfCurrentToken), termNode)
        if termNode == None:
            return None
        
        recentNode.add_child(termNode)

    return recentNode


#Term parser ----------------

#Parse a term that contains a mulOP. We parse the term before the mulop and then add it along with the mulop. After that we parse the factor after the mulop
def _parsemulOP(tokens, indexOfCurrentToken, recentNode, mulOP, indexOfMulop, keyIndexAfterMulOP):
    distanceToTokenAfterOp = 1
    termNode = ASTNode("Term")

    items = list(tokens.items()) #Turn the dict into a list so we can cut it
    beforeMulOP = items[:indexOfMulop] #Cut the tokens before the mulOP
    afterMulOP = items[indexOfMulop+distanceToTokenAfterOp:]#cut after the mulOP

    beforeMulOPTokens = dict(beforeMulOP)
    afterMulOPTokens = dict(afterMulOP)

    termNode = _parseTerm(beforeMulOPTokens, str(indexOfCurrentToken), termNode)

    if termNode == None: #if it isn't a valid term
        return None
    
    recentNode.add_child(termNode)
    recentNode.add_child(ASTNode(mulOP))

    factorNode = ASTNode("Factor")
    
    factorNode = (_parseFactor(afterMulOPTokens, str(int(keyIndexAfterMulOP) 
                  + distanceToTokenAfterOp), factorNode))#We use a keyIndex here because we can't just use i + 1, we need to use the keyIndex of the token after the mulOP.
                                                        #Mainly just for when we have cut open dictionaries a lot

    if factorNode == None: #if it isn't a valid factor
        return None
    
    recentNode.add_child(factorNode)

    return recentNode

    
#Parses through terms, and depending on if there is a mulOP call the mulOP parser or the factor parser
def _parseTerm(tokens, indexOfCurrentToken, recentNode):
    mulOP, index_of_last_mulOP, KeyIndex_for_after_token_split = index_finder(tokens, "mulOP")

    if mulOP != '':
        recentNode = _parsemulOP(tokens, indexOfCurrentToken, recentNode, mulOP, index_of_last_mulOP, KeyIndex_for_after_token_split)
        if recentNode == None:
            return None

    else:
        factorNode = ASTNode("Factor")
        factorNode = _parseFactor(tokens, str(indexOfCurrentToken), factorNode)

        if factorNode == None:
            return None

        recentNode.add_child(factorNode)

    return recentNode



#Factor parser ---------------

#Finding the index of the closing paren, and if there is one
def _closingParenLocator(tokens):
    index_of_closing_paren = 0
    isclosingparen = False

    for keyIndex in tokens:
        if tokens[keyIndex][cc.TOKEN_INDEX] == ")": #Look for first closing paren
            isclosingparen = True
            break

        index_of_closing_paren += 1

    return isclosingparen, index_of_closing_paren

#Will parse through a (expr), makes sure there is a closing paren before looking through, Then cuts the dict to just an expr and parses it
#Add first the opening paren, then the expr node, then the closing paren
def _parseFactorParen(tokens, indexOfCurrentToken, recentNode):
    distanceToStartOfExpr = 1

    recentNode.add_child(ASTNode("("))

    isclosingparen, index_of_closing_paren = _closingParenLocator(tokens) #Finds the closing paren

    if isclosingparen == False:
        return None
    
    items = list(tokens.items())
    between_parens = items[distanceToStartOfExpr:index_of_closing_paren] #Want to cut the parens our of the tokens we pass to expr parser
    between_parens_tokens = dict(between_parens) 

    exprNode = ASTNode("Expr")

    exprNode = _parseExpr(between_parens_tokens, str(int(indexOfCurrentToken) + distanceToStartOfExpr), exprNode)#Want to parse through the expr between the parens, we pass the tokens, the index of the first token and our node

    if exprNode == None:
        return None
    
    recentNode.add_child(exprNode)
    recentNode.add_child(ASTNode(")"))

    return recentNode

#Looks for numbers, IDs, and openParen.
def _parseFactor(tokens, indexOfCurrentToken, recentNode): 

    if len(tokens) == 0: #If we call this and there are no tokens, it means the grammar has a incorrect operator setup Ex: '1 + 2 +' or '* 1 + 2'
        return None
    
    if tokens[indexOfCurrentToken][cc.TOKEN_TYPE_INDEX] == "number":
        numberNode = ASTNode(tokens[indexOfCurrentToken][1])
        recentNode.add_child(numberNode)
        return recentNode
    
    elif tokens[indexOfCurrentToken][cc.TOKEN_TYPE_INDEX] == "identifier":
        idNode = ASTNode(tokens[indexOfCurrentToken][1])
        recentNode.add_child(idNode)
        return recentNode
    
    elif tokens[indexOfCurrentToken][cc.TOKEN_INDEX] == "(":
        return _parseFactorParen(tokens, indexOfCurrentToken, recentNode)
    
    else:
        return None
        
#Function will find the last index of mulOP or addOP and return it
def index_finder(tokens, operatorType):
    operator = ''
    OPIndex = 0
    lastOPIndex = 0
    keyIndexAfterOp = str(0)

    number_of_open_paren = 0
    for keyIndex in tokens:
        if tokens[keyIndex][cc.TOKEN_TYPE_INDEX] == operatorType: #Either a mulOP or addOP
            if number_of_open_paren == 0: #if there are no open parens and the token is a mulOP or addOP. we for now can say that is the last operator
                operator = tokens[keyIndex][1]
                lastOPIndex = OPIndex
                keyIndexAfterOp = keyIndex

        elif tokens[keyIndex][cc.TOKEN_INDEX] == "(":
            number_of_open_paren += 1

        elif tokens[keyIndex][cc.TOKEN_INDEX] == ")":
            number_of_open_paren -= 1

        OPIndex += 1

    return operator, lastOPIndex, keyIndexAfterOp

