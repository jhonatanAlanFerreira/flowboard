from llama_cpp import LlamaGrammar

WORKFLOW_JSON_GRAMMAR = LlamaGrammar.from_string(r"""
root ::= res

res ::= "{" ws "\"workflow\"" ws ":" ws workflow "}"

workflow ::= "{" ws "\"name\"" ws ":" ws string "," ws "\"lists\"" ws ":" ws listlist "}"

listlist ::= "[" ws "]" | "[" ws list (ws "," ws list)* ws "]"

list ::= "{" ws "\"name\"" ws ":" ws string "," ws "\"tasks\"" ws ":" ws tasklist "}"

tasklist ::= "[" ws "]" | "[" ws task (ws "," ws task)* ws "]"

task ::= "{" ws "\"description\"" ws ":" ws string "}"

string ::= "\"" ([^"\\\x7F\x00-\x1F] | "\\" (["\\/bfnrt] | "u" [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F] [0-9a-fA-F]))* "\""

ws ::= [ \t\n]*
""")
