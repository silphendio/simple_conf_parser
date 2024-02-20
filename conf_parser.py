from tokenizer import *
import re
# alternative regex (forbid starting digit): "[^\W0-9]\w*")
re_keyname = re.compile("\w+")

# parse tokens

def parse_value_id(tokens: list[Token], i: int = 0):
    t = tokens[i].type
    if t in [STRING, CHUNK]:
        try:
            return (i+1, parse_primitive(tokens[i]))
        except ValueError:
            err(tokens[i].index, "couldn't read primitive: " + tokens[i].value)
    elif t == ARR_START:
        return parse_array_id(tokens, i+1)
    elif t == OBJ_START:
        return parse_obj_id(tokens, i+1)
    else: err(tokens[i].index, "expected '[', '{' or primitive")

def parse_array_id(tokens: list[Token], i: int):
    array = []
    while i < len(tokens):
        if tokens[i].type == ARR_END:
            return i+1, array
        else:
            i, value = parse_value_id(tokens, i)
            array.append(value)
    return array

def parse_obj_id(tokens: list[Token], i: int):
    obj = {}
    while i < len(tokens):
        if tokens[i].type == OBJ_END:
            return i+1, obj

        if i >= len(tokens) + 2: err(tokens[i].index, "missing data")
        a, sep = tokens[i: i+2]

        try:
            key = parse_key(a)
        except ValueError as e:
            err(a.index, e.args[0])
        
        if sep.type != OBJ_ASSIGN: err(tokens[i].index, "missing colon after key")
        
        i, value = parse_value_id(tokens, i+2)
        obj[key] = value


def parse_key(tok: Token):
    if tok.type == CHUNK:
        if not re.fullmatch(re_keyname, tok.value):
            raise ValueError("invalid identifier")
        return tok.value
    elif tok.type == STRING:
        return tok.value.encode('raw_unicode_escape').decode('unicode_escape')
    else: raise ValueError("expected identifier")

def parse_primitive(tok: Token):
    if tok.type == CHUNK:
        if tok.value == "null":
            return None
        if tok.value == "true":
            return True
        if tok.value == "false":
            return False
        else:
            return str_to_number(tok.value)#literal_eval(tok.value)
    elif tok.type == STRING:
        return tok.value.encode('raw_unicode_escape').decode('unicode_escape')
    else: raise ValueError("expected identifier")

# helper functions
def index_to_coordinates(s: str, index: int):
    """Returns (line_number, col) of `index` in `s`."""
    if not len(s):
        return 1, 1
    sp = s[:index+1].splitlines(keepends=True)
    return len(sp), len(sp[-1])

def str_to_number(x):
    try:
        return int(x, 0) # this allows hex & binaary, but forbids leading zeros
        # (that means a number with leading zeros will get parsed as float)
    except ValueError: pass
    try:
        return float(x)
    except ValueError: pass

    # if even this fails, we keep the Exception
    return complex(x)


def loads(json_str: str) -> dict:
    try:
        tokens = tokenize(json_str)
        # auto-detect top-level object without curly braces
        if tokens[1].type == OBJ_ASSIGN:
            tokens.append(make_token(len(json_str), OBJ_END))
            i, res = parse_obj_id(tokens, 0)
        i, res = parse_value_id(tokens, 0)
        assert(i == len(tokens))
        return res
    except ValueError as e:
        line, col = index_to_coordinates(json_str, e.args[0]['index'])
        print(f"error while loading config: at {line}:{col}: {e.args[0]['msg']}")


_TAB = '\t'
# serialize
def dumps_array(arr, indent = 0) -> str:
    s = []
    for val in arr:
        s.append('\t' * indent + dumps_value(val, indent))
    return '\n'.join(s)

def dumps_obj(d, indent = 0) -> str:
    s = []
    for key, val in d.items():
        s.append('\t' * indent + key_str(key) + ": " + dumps_value(val, indent))
    return '\n'.join(s)

def dumps_value(val, indent = 0):
    if isinstance(val, dict):
        return f"{{\n{dumps_obj(val, indent + 1)}\n{_TAB * indent}}}"
    elif isinstance(val, list):
        return f"[\n{dumps_array(val, indent + 1)}\n{_TAB * indent}]"
    else:
        return repr(val)

def key_str(key: str):
    if re.fullmatch(re_keyname, key):
        return key
    else:
        return repr(key)

def dumps(obj, add_braces = False):
    if isinstance(obj, dict) and not add_braces:
        return dumps_obj(obj)
    else: return dumps_value(obj)