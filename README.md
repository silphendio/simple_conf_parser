# Silphy's Simple Configuration Language

SSCL is a superset of JSON.

This repository contains a reference implementation in Python. It can read a string into a python dict or turn a dict back into a formatted string, just like the `json.loads` and `json.dumps` methods.

## The file format
The format is based on JSON, with the following changes:
- comments: everything from a `#` to the end of the line is ignored
- unicode whitespace characters count as whitespace too.
- commas are optional and can be replaced any kind of whitespace.
- for top-level objects or arrays, no braces are required
- optionally unquoted object keys: Only numbers, letters and `_` are allowed in unquoted keys (Equivalent to the python regular expression `r'\w+'` ). Those are always interpreted as strings.
- numbers can be in any format that python supports: int, float or complex. (Starting an integer number with 0 is forbidden, but the parser currently just falls back to float)

The following features are still subject to change.
- `=` can be used instead of `:`. I don't know why I included that.
- commas can be replaced with semicolons. Since those are treated like whitespace anyway, I'm not sure how useful this is.
- strings can span multiple lines. Escaping a newline or using different quotes is currently neither required nor supported.

The following things are *not* supported, but might be added later:
- c-style comments
- python-style docstrings
- comments starting with a semicolon

Simple configuration files have no specified extensions, because there a far too many out there. If this unexpectly gets popular, I might revisit the idea.
For now, I recommend saving configuration files as `.conf`. That format isn't defined, and it's clear that it's meant to be a configuration file.
`.yaml` is also an option, because simple conf files are largely a subset of YAML and thus gets syntax highlighting in fancy editors.

## installation
pypi package is coming soon. For now, just drop the `conf_parser.py` and `tokenizer.py` into a python project.

## usage
Use the `loads` method. It returns a dict or throws and error (including the line/col) where it happened.
```
import sscl
obj = sscl.loads(conf_str)
print(obj.dumps())
```

## how it looks like
Here's an example SSCL file
```
unquoted_keys: 'single quotes are "here"'
"quoted keys": "it's double quotes now"
hexadecimal: 0xdecaf # this is a comments
multiline: "no \\n here \
or there\
but
here
" # equivalent to 'no \\n here or therebut\nhere\n'

'number formats': [.123, 123., 1e3, inf, nan, -inf]
ünicode_kéys: '試験'
nested_objects: {
  obj: { a: 2, b: 4,
    c: { a: 1, b: 2, c: [1, 2, 3] }
  }
# mixed types, optional comma
  x: [  {x: 0, y: "null"  z: null}, false, [] ]
}
matrix: [
  [ 1 2 3 ]
  [ 4 5 6 ]
  [ 7 8 9 ]
]

```

## performance
The parser is written in pure python. Because because of that, it's about 40x slower than python's `json` module.

This can be veryfied with the `bench.py` script and some json files [these](https://github.com/jdorfman/awesome-json-datasets).


## Why?
There are many different configuration file formats out there, and I don't like any of them.
- *YAML*:
  
  The format is overly complicated and it allows unquoted strings. I find this problematic because it's too easy for something to get misinterpreted that way.
  I'm also not a big fan of the syntax. Why do elements of an object of a list get the same level of indentation as simple elements?
  That said, strings can just be quoted and YAML offers optional JSON-style syntax. I'm not sure this makes things better.
- *TOML*:
  
  I just don't like the syntax for nested lists and subtables.
- *JSON5*:

- JSON is obviously unsuited for configuration files, but JSON5 is almost perfect.
  It supports comments, trailing commas and unquoted keys. (Those are always treated as strings and therefore unambiguous.)
  But since it needs to be compatible with Javascript, there are a few annoyances too:
  - The commas are absolutely superfluous and should not be required.
  - Enclosing the entire configuration file in curly braces just doesn't make sense to me.
