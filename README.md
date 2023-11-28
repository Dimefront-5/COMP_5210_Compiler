# COMP_5210_Compiler

This compiler was created for the COMP 5210 class at Auburn University. It is a custom compiler for a subset of the C language. Below is a description of the compiler and how to use it. If you would like more details on the compiler, please see the [design document](Design_Document.pdf).

Compiles our input into assembly code and outputs it to a .asm file and will output the following, based on what flag you provide: Tokens, Abstract Syntax Tree, Symbol Table, Three Address Code, optimized Three Address Code, control flow graph, dominator graph

usage: 
<pre><code>  Compiler.py [-h] [-t] [-p] [-s] [-a] [-o] [-g] [-d] File </code></pre>

positional arguments:
  <pre><code>  File        a valid c input file </code></pre><br>

options:
  <pre><code>  -h, --help  show this help message and exit  <br>
  -t          outputs the tokenized version of the input file <br>
  -p          outputs the abstract syntax tree of the input file <br>
  -s          outputs the symbol table of the input table <br>
  -a          outputs the three address code of the input file <br>
  -o          outputs the optimized three address code of the input file <br>
  -g          outputs the flow graph of the input file <br>
  -d          outputs the dominator graph of the input file </code></pre><br>



# WAR EAGLE!
