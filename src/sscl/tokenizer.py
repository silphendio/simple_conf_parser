from dataclasses import dataclass

# tokenize

ARR_START, ARR_END, OBJ_START, OBJ_END, OBJ_ASSIGN, STRING, CHUNK = range(7)
TOKEN_NAMES = ["ARR_START", "ARR_END", "OBJ_START", "OBJ_END", "OBJ_ASSIGN", "STRING", "CHUNK"]

@dataclass
class Token:
    type: int
    value: str
    index: int

    def type_str(self):
        return TOKEN_NAMES[self.type]

def make_token(index, type, value=""):
    return Token(index=index, type=type, value=value)


def tokenize(conf_str):
    tokens: list[Token] = []
    i = 0
    
    while i < len(conf_str):
        c = conf_str[i]
        if c == '[':
            tokens.append(make_token(i, ARR_START))
        elif c == ']':
            tokens.append(make_token(i, ARR_END))
        elif c == '{':
            tokens.append(make_token(i, OBJ_START))
        elif c == '}':
            tokens.append(make_token(i, OBJ_END))
        elif c in ":=":
            tokens.append(make_token(i, OBJ_ASSIGN))
        elif c in "'\"":
            j = _find_unescaped_match(conf_str, i+1, c)
            tokens.append(make_token(i, STRING, conf_str[i+1: j]))
            i = j
        elif c == '#': # comment
            i = _find_line_end(conf_str, i+1) 
        elif c.isspace() or c in ",;":
            # ignore whitespace and commas, semicolons too for good measure
            pass
        else :
            j = _find_chunk_end(conf_str, i+1) 
            tokens.append(make_token(i, CHUNK, conf_str[i: j]))
            i = j-1
            
        i += 1
    return tokens

# this needs to handle strings like "\\\\\\\"" too
def _find_unescaped_match(s: str, i: int, c) -> int:
    j = i # for error handling
    escape = False
    while i < len(s):
        if s[i] == '\\':
            escape = not escape
        elif s[i] == c and not escape:
            return i
        else:
            escape = False
        i += 1
    err(j, "no matching quote found " + s[j:])

def _find_line_end(s: str, i: int) -> int:
    while i < len(s):
        if s[i] == '\n':
            return i
        i += 1
    return i

def _find_chunk_end(s: str, i: int) -> int:
    while i < len(s):
        if s[i].isspace() or s[i] in "[]{},;:=#'\"":
            return i
        i += 1
    return i

def err(index: int, msg: str):
    raise ValueError({"index":index , "msg": msg})
