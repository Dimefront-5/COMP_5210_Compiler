'''
-@author: Tyler Ray
-@date: 9/6/2023

- Will parse through our token list and output a parse tree
- ***WORK IN PROGRESS***
'''

import re
#grammar for our parser

grammar = {
    '<expr>': ['<term> <addop> <expr>', '<term>'],
    '<term>': ['<factor> <multop> <term>', '<factor>'],
    '<factor>': ['<digits>', '( <expr> )'],
    '<digits>': ['<digit><digits>', '<digit>'],
    '<addop>': ['+', '-'],
    '<multop>': ['*', '/'],
    '<digit>': ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
}
