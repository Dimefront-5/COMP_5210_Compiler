'''
-@author: Tyler Ray
-@date: 10/26/2023

- A bunch of constants that are used throughout the compiler
'''

#dictionary indicies
TOKEN_TYPE_INDEX = 0
TOKEN_INDEX = 1
LINE_NUMBER_INDEX = 2
COLUMN_NUMBER_INDEX = 3


#Common things we reference
exprOps = r'\+|\-|\/|\*'
numbers = r'^[-+]?\d*\.?\d+$'
identifiers = r'^[A-Za-z_][\w_]*$'