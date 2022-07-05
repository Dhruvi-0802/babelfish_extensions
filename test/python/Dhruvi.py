x="Hello world"
print(x)

print("trying out python")

for i in range(5):
    print(i)

import os
d=os.environ
#print(d.keys())

file1=open("start.py","r")
readfile=file1.read()

print(readfile)
if "pytest" in readfile:
    print("Found")
else:
    print("Not found")

file1.close()

