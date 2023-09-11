'''
-@author: Tyler Ray
-@date: 9/11/2023

- Will parse through our token list and output a parse tree
- ***WORK IN PROGRESS***
'''
import compilerConstants as cc

#grammar for our parser
grammar = {
    'Expr': ['Expr + Term', 'Expr - Term', 'Term'],
    'Term': ['Term * Factor', 'Term / Factor', 'Factor'],
    'Factor': ['num', '(Expr)', 'id'],
    'num': [r'^[\d]+$ | ^[\d]+\.[\d]+$'],
    'id': [r'^[A-Za-z_][\w_]*$'] 
}

#ASTNode class ----------------
#I had chatGPT generate this for me
class ASTNode:
    def __init__(self, value=None):
        self.value = value          
        self.children = []          # List of child nodes

    def add_child(self, child_node):
        self.children.append(child_node)

    def __str__(self, level=0):
        result = "-" * level + self.value + "\n"

        for child in self.children:
            result += child.__str__(level + 1)

        return result


#main function for the parser
def parser(tokens):
    parseTree = ASTNode("Expr") #Start with an expr node
    indexofFirstToken = 0
    parseTree = _parseExpr(tokens, str(indexofFirstToken), parseTree)

    isASTValid = _parseValidation(tokens, parseTree)

    if isASTValid == True:
        return parseTree
    else:
        return False
    
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

#Expr parser ----------------
#Will parse through addOP expressions, then will add the addOP and parse a term
def _parseaddOP(tokens, indexOfCurrentToken, recentNode, addOP, indexOfAddop, keyIndexAfterAddOP):
    distanceToTokenAfterOp = 1
    exprNode = ASTNode("Expr")

    listOfTokens = list(tokens.items())
    beforeAddOP = listOfTokens[:indexOfAddop]
    afterAddOP = listOfTokens[indexOfAddop+distanceToTokenAfterOp:] #We want to cut out the addOP token from the tokens we pass to the expr parser

    beforeAddOPTokens = dict(beforeAddOP)
    afterAddOPTokens = dict(afterAddOP)

    exprNode = _parseExpr(beforeAddOPTokens, str(indexOfCurrentToken), exprNode)

    if exprNode == False:
        return False
    
    recentNode.add_child(exprNode)
    recentNode.add_child(ASTNode(addOP))


    termNode = ASTNode("Term")
    termNode = _parseTerm(afterAddOPTokens, str(int(keyIndexAfterAddOP)+distanceToTokenAfterOp), termNode) #Same as the term parser, we use a keyIndex here because we can't just use i + 1, we need to use the keyIndex of the token after the addOP.
    recentNode.add_child(termNode)

    return recentNode

#Parses through exprs, and depending on if there is a addOP call the addOP parser or the term parser
def _parseExpr(tokens, indexOfCurrentToken, recentNode):
    addOP, indexOfLastAddOP, keyIndexOfTokenAfterOp = index_finder(tokens, "addOP")

    if addOP != '':
        recentNode = _parseaddOP(tokens, indexOfCurrentToken, recentNode, addOP, indexOfLastAddOP, keyIndexOfTokenAfterOp)

    else:
        termNode = ASTNode("Term")
        termNode = _parseTerm(tokens, str(indexOfCurrentToken), termNode)
        if termNode == False:
            return False
        
        recentNode.add_child(termNode)

    return recentNode


#Term parser ----------------

#Parses a mulOP term, then will add the mulOP and parse a factor
def _parsemulOP(tokens, indexOfCurrentToken, recentNode, mulOP, indexOfMulop, keyIndexAfterMulOP):
    distanceToTokenAfterOp = 1
    termNode = ASTNode("Term")

    items = list(tokens.items())
    beforeMulOP = items[:indexOfMulop]
    afterMulOP = items[indexOfMulop+distanceToTokenAfterOp:]

    beforeMulOPTokens = dict(beforeMulOP)
    afterMulOPTokens = dict(afterMulOP)

    termNode = _parseTerm(beforeMulOPTokens, str(indexOfCurrentToken), termNode)

    if termNode == False:
        return False
    
    recentNode.add_child(termNode)
    recentNode.add_child(ASTNode(mulOP))

    factorNode = ASTNode("Factor")
    
    factorNode = (_parseFactor(afterMulOPTokens, str(int(keyIndexAfterMulOP) + distanceToTokenAfterOp), factorNode))#We use a keyIndex here because we can't just use i + 1, we need to use the keyIndex of the token after the mulOP.
                                                                                     #Mainly just for when we have cut open dictionaries a lot
    recentNode.add_child(factorNode)

    return recentNode

    
#Parses through terms, and depending on if there is a mulOP call the mulOP parser or the factor parser
def _parseTerm(tokens, indexOfCurrentToken, recentNode):
    mulOP, index_of_last_mulOP, KeyIndex_for_after_token_split = index_finder(tokens, "mulOP")

    if mulOP != '':
        recentNode = _parsemulOP(tokens, indexOfCurrentToken, recentNode, mulOP, index_of_last_mulOP, KeyIndex_for_after_token_split)

    else:
        factorNode = ASTNode("Factor")
        factorNode = _parseFactor(tokens, str(indexOfCurrentToken), factorNode)

        if factorNode == False:
            return False

        recentNode.add_child(factorNode)

    return recentNode



#Factor parser ---------------

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
def _parseFactorParen(tokens, indexOfCurrentToken, recentNode):
    distanceToStartOfExpr = 1

    recentNode.add_child(ASTNode("("))

    isclosingparen, index_of_closing_paren = _closingParenLocator(tokens)

    if isclosingparen == False:
        return False
    
    items = list(tokens.items())
    between_parens = items[distanceToStartOfExpr:index_of_closing_paren] #Want to cut the parens our of the tokens we pass to expr parser
    between_parens_tokens = dict(between_parens) 

    exprNode = ASTNode("Expr")

    exprNode = _parseExpr(between_parens_tokens, str(int(indexOfCurrentToken) + distanceToStartOfExpr), exprNode)

    if exprNode == False:
        return False
    
    recentNode.add_child(exprNode)
    recentNode.add_child(ASTNode(")"))

    return recentNode

#Looks for numbers, IDs, and openParen.
def _parseFactor(tokens, indexOfCurrentToken, recentNode): 

    if len(tokens) == 0: #If we call this and there are no tokens, it means the grammar has a incorrect operator setup Ex: '1 + 2 +' or '* 1 + 2'
        return False
    
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
        return False
        
#Function will find the last index of mulOP or addOP and return it
def index_finder(tokens, operatorType):
    operator = ''
    mulOPIndex = 0
    lastmulOPIndex = 0
    keyIndexAfterOp = str(0)

    number_of_open_paren = 0
    for keyIndex in tokens:
        if tokens[keyIndex][cc.TOKEN_TYPE_INDEX] == operatorType: #Either a mulOP or addOP
            if number_of_open_paren == 0:
                operator = tokens[keyIndex][1]
                lastmulOPIndex = mulOPIndex
                keyIndexAfterOp = keyIndex

        elif tokens[keyIndex][cc.TOKEN_INDEX] == "(":
            number_of_open_paren += 1

        elif tokens[keyIndex][cc.TOKEN_INDEX] == ")":
            number_of_open_paren -= 1

        mulOPIndex += 1

    return operator, lastmulOPIndex, keyIndexAfterOp

