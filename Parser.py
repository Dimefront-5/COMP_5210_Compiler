'''
-@author: Tyler Ray
-@date: 9/8/2023

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



def parser(tokens):
    print(tokens)
    parseTree = ASTNode("Expr")
    parse_term(tokens, str(0), parseTree)
    return parseTree


def parse_expr(tokens, i, RecentNode):
    return

def parse_term(tokens, i , RecentNode): #Not working
    termNode = ASTNode("Term")
    i = int(i)
    print(tokens[str(i+1)][1], i)
    if tokens[str(i+1)][1] == "*":
        i+= 1
        print(tokens)
        termNode = parse_term(tokens, str(i), termNode)
        RecentNode.add_child(termNode)
        RecentNode.add_child(ASTNode("*"))
        factorNode = parse_factor(tokens, str(2), RecentNode)
        RecentNode.add_child(factorNode)
        return RecentNode

    elif tokens[str(i+1)][1] == "/":
        parse_term(tokens, i, termNode)
        RecentNode.add_child(ASTNode("/"))
    else:
        print(tokens)
        termNode = parse_factor(tokens, str(i), termNode)
        if termNode == False:
            return False
    
    RecentNode.add_child(termNode)
    return RecentNode

def parse_factor(tokens, i, RecentNode): 
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
