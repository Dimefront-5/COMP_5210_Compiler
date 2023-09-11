'''
-@author: Tyler Ray
-@date: 9/11/2023

- Will parse through our token list and output a parse tree
- ***WORK IN PROGRESS***
'''

#grammar for our parser
grammar = {
    'Expr': ['Expr + Term', 'Expr - Term', 'Term'],
    'Term': ['Term * Factor', 'Term / Factor', 'Factor'],
    'Factor': ['num', '(Expr)', 'id'],
    'num': [r'^[\d]+$ | ^[\d]+\.[\d]+$'],
    'id': [r'^[A-Za-z_][\w_]*$'] 
}

#main function for the parser
def parser(tokens):
    parseTree = ASTNode("Expr") #Start with an expr node
    parseTree = parse_expr(tokens, str(0), parseTree)

    is_ast_valid = parse_validator(tokens, parseTree)

    if is_ast_valid:
        return parseTree
    else:
        return False
    
#Function will find every leaf node, if the number of leaf nodes is equal to the number of tokens it is valid syntax.
def parse_validator(tokens, parsetree):
    length_of_tokens = len(tokens)
    count = 0
    number_of_leaf_nodes = find_leaf_nodes(parsetree, count)

    if number_of_leaf_nodes != length_of_tokens:
        return False
    
    return True

#Finds every leaf node
def find_leaf_nodes(node, count):
    
    if len(node.children) == 0:
        count += 1
        return count

    else:
        for child in node.children:
            count = find_leaf_nodes(child, count)

    return count

#Expr parser ----------------
#Will parse through addOP expressions, then will add the addOP and parse a term
def parse_expr_addOP(tokens, i, RecentNode, addOP, index_of_addOP, KeyIndex):
    exprNode = ASTNode("Expr")

    items = list(tokens.items())
    beforeAddOP = items[:index_of_addOP]
    afterAddOP = items[index_of_addOP+1:]

    beforeAddOPTokens = dict(beforeAddOP)
    afterAddOPTokens = dict(afterAddOP)

    exprNode = parse_expr(beforeAddOPTokens, str(i), exprNode)

    if exprNode == False:
        return False
    
    RecentNode.add_child(exprNode)
    RecentNode.add_child(ASTNode(addOP))


    termNode = ASTNode("Term")
    termNode = parse_term(afterAddOPTokens, str(int(KeyIndex)+1), termNode) #Same as the term parser, we use a keyIndex here because we can't just use i + 1, we need to use the keyIndex of the token after the addOP.
    RecentNode.add_child(termNode)

    return RecentNode

#Parses through exprs, and depending on if there is a addOP call the addOP parser or the term parser
def parse_expr(tokens, i, RecentNode):
    addOP, index_of_last_addOP, keyIndex_for_after_token_split = index_finder(tokens, "addOP")

    if addOP != '':
        RecentNode = parse_expr_addOP(tokens, i, RecentNode, addOP, index_of_last_addOP, keyIndex_for_after_token_split)

    else:
        termNode = ASTNode("Term")
        termNode = parse_term(tokens, str(i), termNode)
        if termNode == False:
            return False
        
        RecentNode.add_child(termNode)

    return RecentNode


#Term parser ----------------

#Parses a mulOP term, then will add the mulOP and parse a factor
def parse_term_mulOP(tokens, i, RecentNode, mulOP, index_of_mulOP, keyIndex):
    termNode = ASTNode("Term")

    items = list(tokens.items())
    beforeMulOP = items[:index_of_mulOP]
    afterMulOP = items[index_of_mulOP+1:]

    beforeMulOPTokens = dict(beforeMulOP)
    afterMulOPTokens = dict(afterMulOP)

    termNode = parse_term(beforeMulOPTokens, str(i), termNode)

    if termNode == False:
        return False
    
    RecentNode.add_child(termNode)
    RecentNode.add_child(ASTNode(mulOP))

    factorNode = ASTNode("Factor")
    
    factorNode = (parse_factor(afterMulOPTokens, str(int(keyIndex) + 1), factorNode))#We use a keyIndex here because we can't just use i + 1, we need to use the keyIndex of the token after the mulOP.
                                                                                     #Mainly just for when we have cut open dictionaries a lot
    RecentNode.add_child(factorNode)

    return RecentNode

    
#Parses through terms, and depending on if there is a mulOP call the mulOP parser or the factor parser
def parse_term(tokens, i , RecentNode):
    mulOP, index_of_last_mulOP, KeyIndex_for_after_token_split = index_finder(tokens, "mulOP")

    if mulOP != '':
        RecentNode = parse_term_mulOP(tokens, i, RecentNode, mulOP, index_of_last_mulOP, KeyIndex_for_after_token_split)

    else:
        factorNode = ASTNode("Factor")
        factorNode = parse_factor(tokens, str(i), factorNode)

        if factorNode == False:
            return False

        RecentNode.add_child(factorNode)

    return RecentNode



#Factor parser ---------------

def closing_paren_finder(tokens):
    index_of_closing_paren = 0
    isclosingparen = False
    for keyIndex in tokens:
        if tokens[keyIndex][1] == ")": #Look for first closing paren
            isclosingparen = True
            break

        index_of_closing_paren += 1

    return isclosingparen, index_of_closing_paren

#Will parse through a (expr), makes sure there is a closing paren before looking through, Then cuts the dict to just an expr and parses it
def parse_factor_paren(tokens, i, RecentNode):
    RecentNode.add_child(ASTNode("("))

    isclosingparen, index_of_closing_paren = closing_paren_finder(tokens)

    if isclosingparen == False:
        return False
    
    items = list(tokens.items())
    between_parens = items[1:index_of_closing_paren] #Want to cut the parens our of the tokens we pass to expr parser
    between_parens_tokens = dict(between_parens) 

    exprNode = ASTNode("Expr")

    exprNode = parse_expr(between_parens_tokens, str(int(i) + 1), exprNode)

    if exprNode == False:
        return False
    
    RecentNode.add_child(exprNode)
    RecentNode.add_child(ASTNode(")"))

    return RecentNode

#Looks for numbers, IDs, and openParen.
def parse_factor(tokens, i, RecentNode): 

    if len(tokens) == 0: #If we call this and there are no tokens, it means the grammar has a incorrect operator setup Ex: '1 + 2 +' or '* 1 + 2'
        return False
    
    if tokens[i][0] == "number":
        numberNode = ASTNode(tokens[i][1])
        RecentNode.add_child(numberNode)
        return RecentNode
    
    elif tokens[i][0] == "identifier":
        idNode = ASTNode(tokens[i][1])
        RecentNode.add_child(idNode)
        return RecentNode
    
    elif tokens[i][1] == "(":
        return parse_factor_paren(tokens, i, RecentNode)
    
    else:
        return False
        
#Function will find the last index of mulOP or addOP and return it
def index_finder(tokens, operator_type):
    operator = ''
    index_of_mulOP = 0
    index_of_last_mulOP = 0
    KeyIndex_for_after_token_split = str(0)

    number_of_open_paren = 0
    for keyIndex in tokens:
        if tokens[keyIndex][0] == operator_type: #Either a mulOP or addOP
            if number_of_open_paren == 0:
                operator = tokens[keyIndex][1]
                index_of_last_mulOP = index_of_mulOP
                KeyIndex_for_after_token_split = keyIndex

        elif tokens[keyIndex][1] == "(":
            number_of_open_paren += 1

        elif tokens[keyIndex][1] == ")":
            number_of_open_paren -= 1

        index_of_mulOP += 1

    return operator, index_of_last_mulOP, KeyIndex_for_after_token_split


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
