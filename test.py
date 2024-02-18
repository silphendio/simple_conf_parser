from conf_parser import *
import sys

json_str = open(sys.argv[1], encoding='utf-8').read()
#json_str = '{' + json_str + '}'

try:
    tokens = tokenize(json_str)
    #for tok in tokens:
    #    print(f"{index_to_coordinates(json_str, tok.index)}: {tok.type_str()} {repr(tok.value)}")
    _, res = parse_value_id(tokens, 0)
    print(res)
    print(dumps(res))
except ValueError as e:
    line, col = index_to_coordinates(json_str, e.args[0]['index'])
    print(f"error while loading config: at {line}:{col}: {e.args[0]['msg']}")
