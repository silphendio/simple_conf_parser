from dataclasses import dataclass

import re
# single or double quotes, re.DOTALL for multiline strings
re_string = re.compile(r"""("([^\\"]|(\\.))*")|('([^\\']|(\\.))*')""", re.DOTALL)

# matches all except whitespace, reserved characters or start of comments
re_chunk = re.compile(r"([^\s\[\]{},;:=#'\"]|(/[^/*]))*")

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
            m = re_string.match(conf_str, i)
            if m:
                tokens.append(make_token(i, STRING, m.group()[1:-1]))
                i = m.end() - 1
            else:
                err(i, "no matching quote found ")

        elif c == '#' or conf_str[i:i+2] == '//': # comment
            i = conf_str.find('\n', i)
            if i < 0: 
                i = len(conf_str) - 1
        elif conf_str[i:i+2] == '/*': # multi-line comment
            i = conf_str.find('*/', i) + 1
            if i < 0: 
                i = len(conf_str) - 1

        elif c.isspace() or c in ",;":
            # ignore whitespace and commas, semicolons too for good measure
            pass
        else :
            m = re_chunk.match(conf_str, i)
            if m:
                tokens.append(make_token(i, CHUNK, m.group()))
                i = m.end() - 1
            else:
                tokens.append(make_token(i, CHUNK, conf_str[i:]))
                i = len(conf_str) - 1
            
        i += 1
    return tokens

def err(index: int, msg: str):
    raise ValueError({"index":index , "msg": msg})
