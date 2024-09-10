from __future__ import print_function

project = projects.primary
finds = project.find("PLC Logic", True)
for mem in dir(finds[0].__class__):
    print(mem)
