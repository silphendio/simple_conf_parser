from .tokenizer import *
from typing import Callable
import re
# alternative regex (forbid starting digit): "[^\W0-9]\w*")
re_keyname = re.compile(r"\w+")
re_int = re.compile(r"[-+]?((0[bo])?[0-9]*)|(0x[0-9a-f]*)")


class Args:
    parse_float: Callable[[str], float]
    parse_int: Callable[[str], int]
    object_hook = None
    object_pairs_hook = None

def parse_value_id(tokens: list[Token], i: int, args: Args):
    t = tokens[i].type
    if t in [STRING, CHUNK]:
        try:
            return (i+1, parse_primitive(tokens[i], args))
        except ValueError:
            err(tokens[i].index, "couldn't read primitive: " + tokens[i].value)
    elif t == ARR_START:
        return parse_array_id(tokens, i+1, args)
    elif t == OBJ_START:
        return parse_obj_id(tokens, i+1, args)
    else: err(tokens[i].index, "expected '[', '{' or primitive")           

def parse_array_id(tokens: list[Token], i: int, args: Args):
    array = []
    while i < len(tokens):
        if tokens[i].type == ARR_END:
            return i+1, array
        else:
            i, value = parse_value_id(tokens, i, args)
            array.append(value)
    return array

def parse_obj_id(tokens: list[Token], i: int, args: Args):
    j = i # for error message
    obj = {}
    while i < len(tokens):
        if tokens[i].type == OBJ_END:
            return i+1, obj

        if i >= len(tokens) + 2: err(tokens[i].index, "missing data")
        a, sep = tokens[i: i+2]

        try:
            key = parse_key(a, args)
        except ValueError as e:
            err(a.index, e.args[0])
        
        if sep.type != OBJ_ASSIGN: err(tokens[i].index, "missing colon after key")
        
        i, value = parse_value_id(tokens, i+2, args)
        obj[key] = value
    err(tokens[j].index, "no closing brace found")


def parse_key(tok: Token, args: Args):
    if tok.type == CHUNK:
        if not re.fullmatch(re_keyname, tok.value):
            raise ValueError("invalid identifier")
        return tok.value
    elif tok.type == STRING:
        return tok.value.encode('raw_unicode_escape').decode('unicode_escape')
    else: raise ValueError("expected identifier")

def parse_primitive(tok: Token, args: Args):
    v = tok.value
    if tok.type == CHUNK:
        if v == "null":
            return None
        if v == "true":
            return True
        if v == "false":
            return False
        else: # number
            if re_int.fullmatch(v):
                return args.parse_int(v)
            else:
                return args.parse_float(v)
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

def parse_tokens(tokens: list[Token], args):
    if len(tokens) > 1 and tokens[0].type in [STRING, CHUNK] and  tokens[1].type in [STRING, CHUNK]:
        tokens.append(make_token(-1, ARR_END))
        i, res = parse_array_id(tokens, 0, args)
    
    elif len(tokens) > 2 and tokens[1].type == OBJ_ASSIGN:
        tokens.append(make_token(-1, OBJ_END))
        i, res = parse_obj_id(tokens, 0, args)
    
    else:
        i, res = parse_value_id(tokens, 0, args)
    
    if i < len(tokens):
        err(tokens[-1].index, "parsing finished, but there's still tokens left")
    return res


def loads(text: str, *, object_hook=None, parse_float=None, parse_int=None,
          object_pairs_hook=None, **kw) -> dict:
    # get args
    args = Args()
    args.parse_float = parse_float or float
    args.parse_int = parse_int or (lambda x: int(x, 0))

    # TODO
    args.object_hook = object_hook
    args.object_pairs_hook = object_pairs_hook

    try:
        return parse_tokens(tokenize(text), args)
    except ValueError as e:
        line, col = index_to_coordinates(text, e.args[0]['index'])
        print(f"error while loading config: at {line}:{col}: {e.args[0]['msg']}")

def load(fp, **kw):
    return loads(fp.read(), **kw)
