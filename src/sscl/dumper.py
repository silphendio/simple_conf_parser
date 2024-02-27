import re
from .parser import re_keyname

def dump_float(x):
    if x == float("inf"):
        return "Infinity"
    if x == float("-inf"):
        return "-Infinity"
    if x == float("NaN"):
        return "NaN"
    return str(x)

class Args:
    skipkeys=False # skip non-str keys, otherwise throw error
    ensure_ascii=True # escape unicode
    check_circular=True
    indent=None
    indent_str = ''
    separators=(' ', ':')
    default=repr
    sort_keys=False
    add_braces = False
    forbidden_refs = set()
    dump_int = str
    dump_float = dump_float
    

def dumps_array(arr: list, args: Args, indent = 0) -> str:
    s = []
    for val in arr:
        s.append(args.indent_str * indent + dumps_value(val, args, indent))
    return args.separators[0].join(s)

def dumps_obj(obj: dict, args: Args, indent = 0) -> str:
    s = []
    items = obj.items()
    if args.sort_keys:
        items = sorted(items)
    for key, val in items:
        if not isinstance(key, str):
            if args.skipkeys:
                continue
            raise ValueError("invalid key found: " + repr(key))
        s.append(args.indent_str * indent + key_str(key, args) + args.separators[1] + dumps_value(val, args, indent))
    return args.separators[0].join(s)

def dumps_value(val, args: Args, indent: int = 0):
    # primitive types
    if isinstance(val, int):
        return args.dump_int(val)
    if isinstance(val, float):
        return args.dump_float(val)
    if isinstance(val, bool):
        return "true" if val else "false"
    if val is None:
        return "null"
    if isinstance(val, str):
        if args.ensure_ascii:
            val = val.encode('unicode_escape').decode("ascii")
        return repr(val)

    # check circular refs
    if args.check_circular and id(val) in args.forbidden_refs:
        raise ValueError("circular reference detected")

    # list or dict (TODO: unify this)
    linebreak = '\n' * (args.indent is not None)
    if isinstance(val, dict):
        if len(val) == 0:
            return "{}"
        args.forbidden_refs.add(id(val))
        obj = dumps_obj(val, args, indent + 1)
        args.forbidden_refs.remove(id(val))
        
        return '{' + linebreak +  obj + linebreak + args.indent_str * indent + '}'
    
    if isinstance(val, list) or isinstance(val, tuple):
        if len(val) == 0:
             return "[]"
        args.forbidden_refs.add(id(val))
        arr = dumps_array(val, args, indent + 1)
        args.forbidden_refs.remove(id(val))

        return '[' + linebreak + arr + linebreak + args.indent_str * indent + ']'
    
    # fallback
    return args.default(val)

def key_str(key: str, args: Args):
    if args.ensure_ascii:
        key = key.encode('unicode_escape').decode("ascii")
    if re.fullmatch(re_keyname, key):
        return key
    else:
        return repr(key)

# TODO: use StringIO & f.write() to generate strings

def dumps(obj, *, skipkeys=False, ensure_ascii=False, check_circular=True,
          indent=None, separators=(' ', ': '), default=repr,
          sort_keys=False, add_braces = False, dump_int = str, dump_float = dump_float, **kw):
    # precess args
    args = Args()

    if isinstance(indent, int):
        args.indent_str = ' '*indent
    elif isinstance(indent, str):
        args.indent_str = indent
    args.indent = indent
    
    if indent is not None:
        args.separators = (separators[0].rstrip() + '\n', separators[1])
    else:
        args.separators = separators
    
    args.skipkeys = skipkeys
    args.ensure_ascii = ensure_ascii
    args.check_circular = check_circular
    args.default = default
    args.sort_keys = sort_keys
    args.dump_int = dump_int
    args.dump_float = dump_float

    if isinstance(obj, dict) and not add_braces:
        return dumps_obj(obj, args)
    elif isinstance(obj, list) and not add_braces and len(obj) > 1:
        return dumps_array(obj, args)
    else:
        return dumps_value(obj, args)

def dump(obj, fp, **kw):
    fp.write(dumps(obj, **kw) + "\n")
