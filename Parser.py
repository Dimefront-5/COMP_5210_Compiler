'''
-@author: Tyler Ray
-@date: 9/8/2023

- Will parse through our token list and output a parse tree
- ***WORK IN PROGRESS***
'''
import sys 
#grammar for our parser
grammar = {
    'Expr': ['Expr + Term', 'Expr - Term', 'Term'],
    'Term': ['Term * Factor', 'Term / Factor', 'Factor'],
    'Factor': ['num', '(Expr)', 'id'],
    'num': [r'^[\d]+$ | ^[\d]+\.[\d]+$'],
    'id': [r'^[A-Za-z_][\w_]*$'] 
}



def parser(tokens):
    #print(tokens)
    parseTree = ASTNode("Expr")
    parseTree = parse_expr(tokens, str(0), parseTree)
    return parseTree


def parse_expr_addOP(tokens, i, RecentNode, addOP, index_of_addOP):
    exprNode = ASTNode("Expr")

    items = list(tokens.items())
    beforeAddOP = items[:index_of_addOP]
    afterAddOP = items[index_of_addOP+1:]

    beforeAddOPTokens = dict(beforeAddOP)
    afterAddOPTokens = dict(afterAddOP)
    #print(beforeAddOPTokens, afterAddOPTokens)

    exprNode = parse_expr(beforeAddOPTokens, str(i), exprNode)

    if exprNode == False:
        return False
    
    RecentNode.add_child(exprNode)
    RecentNode.add_child(ASTNode(addOP))

    #print(RecentNode)

    termNode = ASTNode("Term")
    #print(afterAddOPTokens, str(index_of_addOP+1))
    termNode = parse_term(afterAddOPTokens, str(index_of_addOP+1), termNode)
    RecentNode.add_child(termNode)

    return RecentNode

def parse_expr(tokens, i, RecentNode):
    addOP = ''
    i = int(i)
    index_of_addOP = 0
    index_of_last_addOP = 0

    for keyIndex in tokens:
        if tokens[keyIndex][1] == "+" or tokens[keyIndex][1] == "-":
            index_of_last_addOP = index_of_addOP
            #print(index_of_last_addOP, index_of_addOP, "index of addOP")
            addOP = tokens[keyIndex][1]
        index_of_addOP += 1

    if addOP != '':
        #print("here")
        RecentNode = parse_expr_addOP(tokens, i, RecentNode, addOP, index_of_last_addOP)

    else:
        termNode = ASTNode("Term")
        termNode = parse_term(tokens, str(i), termNode)
        if termNode == False:
            return False
        RecentNode.add_child(termNode)

    return RecentNode



def parse_term_mulOP(tokens, i, RecentNode, mulOP, index_of_mulOP, keyIndex):
    termNode = ASTNode("Term")

    items = list(tokens.items())
    beforeMulOP = items[:index_of_mulOP]
    afterMulOP = items[index_of_mulOP+1:]
    beforeMulOPTokens = dict(beforeMulOP)
    afterMulOPTokens = dict(afterMulOP)

    #print(beforeMulOPTokens, afterMulOPTokens, i)

    termNode = parse_term(beforeMulOPTokens, str(i), termNode)

    if termNode == False:
        return False
    
    RecentNode.add_child(termNode)
    RecentNode.add_child(ASTNode(mulOP))

    factorNode = ASTNode("Factor")
    
    factorNode = (parse_factor(afterMulOPTokens, str(int(keyIndex) + 1), factorNode))
    RecentNode.add_child(factorNode)

    return RecentNode
    
    
def parse_term(tokens, i , RecentNode):
    mulOP = ''
    i = int(i)
    index_of_mulOP = 0
    index_of_last_mulOP = 0

    KeyIndex_for_after_token_split = str(0)
    for keyIndex in tokens:
        if tokens[keyIndex][1] == "*" or tokens[keyIndex][1] == "/":
            mulOP = tokens[str(keyIndex)][1]
            index_of_last_mulOP = index_of_mulOP
            KeyIndex_for_after_token_split = keyIndex
        index_of_mulOP += 1
        
    #print(mulOP, index_of_last_mulOP)
    if mulOP != '': #if there is a multiplication or division operator
        RecentNode = parse_term_mulOP(tokens, i, RecentNode, mulOP, index_of_last_mulOP, KeyIndex_for_after_token_split)


    else:
        factorNode = ASTNode("Factor")
        factorNode = parse_factor(tokens, str(i), factorNode)
        if factorNode == False:
            return False

        RecentNode.add_child(factorNode)

    return RecentNode

def parse_factor(tokens, i, RecentNode): 
    #print(i)
    #print(tokens)
    if tokens[i][0] == "number":
        numberNode = ASTNode(tokens[i][1])
        RecentNode.add_child(numberNode)
        return RecentNode
    
    elif tokens[i][0] == "identifier":
        idNode = ASTNode(tokens[i][1])
        RecentNode.add_child(idNode)
        return RecentNode
    
    elif tokens[i][1] == "(":
        RecentNode.add_child(ASTNode("("))

        expr = parse_expr(tokens[1:])
        RecentNode.add_child(expr)

        tokens = tokens[len(expr):]

        if tokens[i][1] == ")":
            RecentNode.add_child(ASTNode(")"))
            return RecentNode
        else:
            return False
    else:
        return False
        
    

#ASTNode class
#I had chatGPT generate this for me
class ASTNode:
    def __init__(self, value=None):
        self.value = value          
        self.children = []          # List of child nodes

    def add_child(self, child_node):
        self.children.append(child_node)

    def __str__(self, level=0):
        result = "  " * (level + 1) + self.value + "\n"

        for child in self.children:
            result += child.__str__(level + 1) #I thank github copilot for this line of code, I am terrible at recursion

        return result
