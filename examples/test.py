import sscl
import sys

file_str = open(sys.argv[1], encoding='utf-8').read()
obj = sscl.loads(file_str)
print(sscl.dumps(obj))
