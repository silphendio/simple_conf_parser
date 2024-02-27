import sscl
import sys

file_str = open(sys.argv[1], encoding='utf-8').read()
print("loading file...")
obj = sscl.loads(file_str)
print("dumping sscl:")
print(sscl.dumps(obj, indent="  "))
