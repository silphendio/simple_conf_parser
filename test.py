from conf_parser import *
import sys

file_str = open(sys.argv[1], encoding='utf-8').read()

try:
    tokens = tokenize(file_str)
    #for tok in tokens:
    #    print(f"{index_to_coordinates(file_str, tok.index)}: {tok.type_str()} {repr(tok.value)}")
    res = parse_tokens(tokens)
    print(res)
    print(dumps(res))
except ValueError as e:
    line, col = index_to_coordinates(file_str, e.args[0]['index'])
    print(f"error while loading config: at {line}:{col}: {e.args[0]['msg']}")
