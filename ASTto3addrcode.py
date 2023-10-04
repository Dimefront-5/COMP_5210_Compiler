'''
-@author: Tyler Ray
-@date: 10/3/2023

- Will take a given AST and convert it to 3 address code
- ***WORK IN PROGRESS***
'''


global threeAddressCode

#the representation of the 3 address code will be a dictionary within dictionaries
#Example: = {'main': {L1: {1: j = 5/6, 2: k = 7+8}, L2: {1: j = 5/6, 2: k = 7+8, etc...}}
threeAddressCode = {}
global symbolTable

global labelCounter
labelCounter = 0
global functionScope
functionScope = 'global'

#Our main function
def converter(AST, SymbolTable):
    global threeAddressCode
    global symbolTable 

    symbolTable = SymbolTable

    declList = AST.return_children() #Grabbing the decl list node

    eachDecl = declList[0].return_children() #Grabbing each individual decleration.

    _iteratingThroughMainDecls(eachDecl)

    return threeAddressCode;


#------ Inward Facing modules

def _iteratingThroughMainDecls(eachDecl):
    for decl in eachDecl:
        _iteratingThroughDecl(decl)

def _iteratingThroughDecl(decl):
    children = decl.return_children()
    for child in children:
        childValue = child.return_value()
        if childValue == 'id':
            _createFunctionInAddressCode(child)


def _createFunctionInAddressCode(idNode):
    global threeAddressCode
    global functionScope
    idName = idNode.return_children()[0]
    idName = idName.return_value()
    threeAddressCode[idName] = {}
    functionScope = idName

