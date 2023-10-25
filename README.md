# COMP_5210_Compiler

Tokenizes input and will output the following, based on what flag you provide: Tokens, Abstract Syntax Tree, Symbol Table, Three Address Code, and optimized Three Address Code

usage: 
<pre><code>  Compiler.py [-h] [-t] [-p] [-s] [-a] [-o] File </code></pre>

a custom python compiler for c files

positional arguments:
  <pre><code>  File        a valid c input file </code></pre><br>

options:
  <pre><code>  -h, --help  show this help message and exit  <br>
  -t          outputs a tokenized version of the input file <br>
  -p          outputs a abstract syntax tree of the input file <br>
  -s          outputs a symbol table of the input table <br>
  -a          outputs the three address code of the input file <br>
  -o          outputs the optimized three address code of the input file <br>
  -g          outputs the flow graph of the input file <br>
  -d          outputs the dominator graph of the input file</code></pre><br>
