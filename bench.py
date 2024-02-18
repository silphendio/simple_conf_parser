# benchmark (measured ~40x slower than python json on my machine)

from conf_parser import *

from timeit import timeit
import json
import sys

number = 10
if len(sys.argv) > 2:
    number = int(sys.argv[2])

# compare results
res1 = {}
res2 = {}

json_str = open(sys.argv[1], encoding='utf-8').read()
def test1():
    res2 = json.loads(json_str)
def test2():
    res1 = loads(json_str, add_braces = False)

print("python json module (for reference)")
print(timeit("test1()", setup="from __main__ import test1", number=number))
print("conf parser")
print(timeit("test2()", setup="from __main__ import test2", number=number))

assert(json.dumps(res1) == json.dumps(res2))

tokens = tokenize(json_str)
def test3():
    tokenize(json_str) 
def test4():
    _, _ = parse_value_id(tokens, 0)

# test tokenize and parse separately
print("tokenize only")
print(timeit("test3()", setup="from __main__ import test3", number=number))
print("parse only")
print(timeit("test4()", setup="from __main__ import test4", number=number))

tokens = tokenize(json_str)


try:
    tokens = tokenize(json_str)
    _, res = parse_value_id(tokens, 0)
except ValueError as e:
    line, col = index_to_coordinates(json_str, e.args[0]['index'])
    print(f"error while loading config: at {line}:{col}: {e.args[0]['msg']}")
