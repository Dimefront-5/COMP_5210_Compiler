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

#Our main function
def converter(AST, SymbolTable):
    global threeAddressCode
    global symbolTable 
    symbolTable = SymbolTable

    declList = AST._return_children() #Grabbing the decl list node

    eachDecl = declList[0]._return_children() #Grabbing each individual decleration.

    _iteratingThroughDecls(eachDecl)

    return threeAddressCode;


#------ Inward Facing modules

def _iteratingThroughDecls(eachDecl):
    for decl in eachDecl:
        print(decl)
