'''
-@author: Tyler Ray
-@date: 9/11/2023

- Will parse through our token list and output a parse tree
- Only works for expr as of right now
- ***WORK IN PROGRESS***
'''
import CompilerConstants as cc
from anytree import RenderTree
'''
Need to change grammar to:
Expr -> Term + Expr, Term - Expr, Term
Term -> Factor * Term, Factor / Term, Factor
Factor -> num, (Expr), id
'''
#grammar for our parser
grammar = {
    'Program': ['declList'],
    'declList': ['decl', 'decl declList'],
    'decl': ['type id (Args) {local_decls stmtList}'],
    'type': ['int', 'void', 'float'],
    'Args': ['Arg', 'Arg, Args'],
    'Arg': ['type id', ''],
    'stmtList': ['stmt', 'stmt stmtList'],
    'stmt': ['return num;'],
    'local_decls': ['local_decl', 'local_decl local_decls'],
    'local_decl': ['type id;'],
    'Expr': ['Expr + Term', 'Expr - Term', 'Term'],
    'Term': ['Term * Factor', 'Term / Factor', 'Factor'],
    'Factor': ['num', '(Expr)', 'id'],
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

    def add_variable(self, name, type, scope):
        self.symbolTable[scope][name] = type

    def add_scope(self, name, fun_type, params):
        if name not in self.symbolTable:
            self.symbolTable[name] = {}  # Create a new scope
        self.symbolTable[name]['return_type'] = fun_type
        self.symbolTable[name]['args'] = params

    def __str__(self):
        output = ""
        for scope in self.symbolTable:
            output += "Scope: " + scope + "\n\t" + "Return Type: " + self.symbolTable[scope]['return_type'] + "\n\tArguments: " + str(self.symbolTable[scope]['args']) + "\n"
            output += "\tVariables:\n"
            for variable in self.symbolTable[scope]:
                if variable != 'return_type' and variable != 'args':
                    output += "\t\t" + variable + ": " + self.symbolTable[scope][variable] + "\n"
            output += "\n"
        return output
    
#ASTNode class ----------------
#I had chatGPT generate this for me
class ASTNode:
    def __init__(self, value=None):
        self.value = value          
        self.children = []          # List of child nodes

    def add_child(self, child_node):
        self.children.append(child_node)

    def __str__(self):
        output = ""
        for pre, fill, node in RenderTree(self):
            output += "%s%s" % (pre, node.value) + "\n"
        return output

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

#Function will find every leaf node, if the number of leaf nodes is equal to the number of tokens it is valid syntax.
def _parseValidation(tokens, parsetree):
    tokensLength = len(tokens)
    count = 0
    numberOfLeafNodes = _findLeafNodes(parsetree, count)

    if numberOfLeafNodes != tokensLength:
        return False
    
    return True

#Finds every leaf node
def _findLeafNodes(node, count):
    
    if len(node.children) == 0:
        count += 1
        return count

    else:
        for child in node.children:
            count = _findLeafNodes(child, count)

    return count

def _parse_program(tokens):
    programNode = ASTNode("Program")
    global index

    while index < len(tokens):
        programNode.add_child(_parse_declList(tokens))
        index+=1

    return programNode

def _parse_declList(tokens):
    global scope
    declListNode = ASTNode("declList")
    
    declNode = _parse_decl(tokens)

    declListNode.add_child(declNode)
    scope = "global"

    return declListNode


#TODO: Not an ideal way to lay this out. I will need to Refactor
def _parse_decl(tokens):
    declNode = ASTNode("decl")
    global index
    global scope

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        typeNode = ASTNode("type")
        typeNode.add_child(ASTNode(tokens[str(index)][cc.TOKEN_INDEX]))
        declNode.add_child(typeNode)
        index += 1
        scope_type = tokens[str(index-1)][cc.TOKEN_INDEX]

        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            idNode = ASTNode("id")
            idNode.add_child(ASTNode(tokens[str(index)][cc.TOKEN_INDEX]))
            declNode.add_child(idNode)
            index += 1
            scope = tokens[str(index-1)][cc.TOKEN_INDEX]
            print(scope)

            if tokens[str(index)][cc.TOKEN_INDEX] == '(':
                index += 1
                argsNode, args = (_parse_Args(tokens))
                declNode.add_child(argsNode)

                symbolTable.add_scope(scope, scope_type, args)

                if tokens[str(index)][cc.TOKEN_INDEX] == ')':
                    index += 1

                    if tokens[str(index)][cc.TOKEN_INDEX] == '{':
                        index += 1
                        declNode.add_child(_parse_local_decls(tokens))
                        declNode.add_child(_parse_stmtList(tokens))
                        index += 1

                        if tokens[str(index)][cc.TOKEN_INDEX] == '}':
                            index += 1
                            return declNode
                        
    return None


def _parse_Args(tokens):
    argsNode = ASTNode("Args")
    argNode, args = _parse_Arg(tokens)
    argsNode.add_child(argNode)  
    return argsNode, args

def _parse_Arg(tokens):
    global index
    global scope
    args = {}
    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        typeNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
        index += 1

        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            typeNode.add_child(ASTNode(tokens[str(index)][cc.TOKEN_INDEX]))
            index += 1
            args[tokens[str(index-1)][cc.TOKEN_INDEX]] = tokens[str(index-2)][cc.TOKEN_INDEX]
            return typeNode, args
    elif tokens[str(index)][cc.TOKEN_INDEX] == ')':
        return ASTNode("")
    
    return None
def _parse_local_decls(tokens):
    local_declsNode = _parse_local_decl(tokens)
    return local_declsNode

def _parse_local_decl(tokens):
    declNode = ASTNode("local_decl")
    global index
    global scope

    if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'type':
        typeNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
        index += 1
        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            typeNode.add_child(ASTNode(tokens[str(index)][cc.TOKEN_INDEX]))
            declNode.add_child(typeNode)
            index += 1
            
            if tokens[str(index)][cc.TOKEN_INDEX] == ';':
                index += 1
                print(tokens, index)
                print(tokens[str(index-2)][cc.TOKEN_INDEX], tokens[str(index-3)][cc.TOKEN_INDEX], scope)
                symbolTable.add_variable(tokens[str(index-2)][cc.TOKEN_INDEX], tokens[str(index-3)][cc.TOKEN_INDEX], scope)
                return declNode
                        
    return None

#stmtList -> stmt stmtList | stmt
def _parse_stmtList(tokens):
    stmtNode = _parse_stmt(tokens)
    return stmtNode

#stmt -> return num;
def _parse_stmt(tokens):
    stmtNode = ASTNode("Stmts")
    global index
    if tokens[str(index)][cc.TOKEN_INDEX] == 'return':
        returnNode = ASTNode("return")
        index += 1
        if tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'number' or tokens[str(index)][cc.TOKEN_TYPE_INDEX] == 'identifier':
            numNode = ASTNode(tokens[str(index)][cc.TOKEN_INDEX])
            returnNode.add_child(numNode)
            stmtNode.add_child(returnNode)
            index += 1
            if tokens[str(index)][cc.TOKEN_INDEX] == ';':
                return stmtNode
    return None

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

