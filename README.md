## A simple parser for configuration files
This parser is compatible with json, but far more lenient. Here's a list of features:
- comments: everything from a `#` to the end of the line is ignored
- commas are optional and can be replaced any kind of whitespace
- top-level braces are automatically added, so they don't need to be in the configuration file. This can be disabled.
- optionally unquoted object keys: Only numbers, letters and '_' are allowed in keys (Equivalent to `r'\w+'` as python regular expression )
- numbers can be in any format that python supports: int, float or complex. (Starting an integer number with 0 is forbidden, but the parser currently just falls back to float)

The following features are still subject to change.
- `=` can be used instead of `:`. For compatibility with other config files.
- commas can be replaced with semicolons. Since those are treated like whitespace anyway, I'm not sure how useful this is.
- strings can span multiple lines. Escaping a newline or using different quotes is currently neither required nor supported.

Simple configuration files have no specified extensions, because there a far too many out there. If this unexpectly gets popular, I might revisit the idea.
For now, I recommend saving configuration files as `.conf`. That format isn't defined, and it's clear that it's meant to be a configuration file.
`.yaml` is also an option, because simple conf files are largely a subset of YAML and thus gets syntax highlighting in fancy editors.

Because this is written in pure python, it's about 40x slower than python's `json` module.
This can be veryfied with the `bench.py` script and some json files [these](https://github.com/jdorfman/awesome-json-datasets).

## installation
pypi package is coming soon. For now, just drop the `conf_parser.py` and `tokenizer.py` in a python project.

## usage
Use the `loads` method. It returns a dict or throws and error (including the line/col) where it happened.
```
import conf_parser
obj = conf_parser.loads(conf_str)
obj2 = conf_parser.loads(json_str, add_braces = False) # for json
```

## how it looks like
Here's an example config file (modified from the [JSON5 example](https://json5.org/#example)
```
unquoted: 'and you can quote me on that'
singleQuotes: 'I can use "double quotes" here'
lineBreaks: "Look, Mom!
No \\n's!",
hexadecimal: 0xdecaf
leadingDecimalPoint: .8675309, andTrailing: 8675309.
positiveSign: +1
trailingComma: 'in objects', andIn: ['arrays',]
"backwardsCompatible": "with JSON"
ünicode_kéys: 1e3 # 3000.0
no_commas: [1 2 3 4 5]
too_many_commas: [1,,2,,3,,4,,5]
# nunbers can be keys too
777: {
    1: [-inf, nan, null]
    2: []
    3: {null: "null"}
}
```


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
  - the {} at the end can be done away with if all configuration files are objects anyway.
