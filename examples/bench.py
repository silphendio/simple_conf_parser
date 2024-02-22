# benchmark (measured ~40x slower than python json on my machine)

from sscl import *

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
    res1 = loads(json_str)

print("python json module (for reference)")
print(timeit("test1()", setup="from __main__ import test1", number=number))
print("conf parser")
print(timeit("test2()", setup="from __main__ import test2", number=number))

assert(json.dumps(res1) == json.dumps(res2))
