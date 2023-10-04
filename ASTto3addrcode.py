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
        elif childValue == 'type':
            pass
        elif childValue == 'Args':
            _create3AddressCodeForArgs(child)


def _createFunctionInAddressCode(idNode):
    global threeAddressCode
    global functionScope

    idName = idNode.return_children()[0]
    idName = idName.return_value()

    threeAddressCode[idName] = {}
    functionScope = idName

def _create3AddressCodeForArgs(argsNode):
    global threeAddressCode
    global functionScope

    args = argsNode.return_children()

    for arg in args:
        argID = arg.return_children()
        if isinstance(argID, list) and argID != []:
            argTypeValue = arg.return_value()
            argIDValue = argID[0].return_value()

            threeAddressCode[functionScope][argIDValue] = ['param', argTypeValue] #We are just going to set the value to param. When we print it out, it will be the param and then the id. But we can't use param as multiple keys

