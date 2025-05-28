"""
PREDICATE
Copyright 2025-present NAVER Corp.
The 3-Clause BSD License

This file shows how decorators can be used to extract data
from an LLM output. programs is a list.
"""

from predicate import *

# We check that value is a string and programs a list
@predicate(guard=lambda value, programs: isinstance(value, str) and isinstance(programs, list))
def check_structure(value, programs):
    # we check if json is present in the value
    pos = value.find("```json")
    p_check(pos != -1)
    # we extract all our JSON structures
    lst = []
    while pos != -1:
        pos += 7
        end = value.find("```", pos)
        if end != -1:
            lst.append(value[pos:end])
            pos = value.find("```json", end)
        else:
            pos = -1
    p_check(lst)
    for p in lst:
        programs.append(p)

@predicate(guard=lambda value, programs: isinstance(value, str) and isinstance(programs, list))
def check_structure(value, programs):
    pos = value.find("```python")
    p_check(pos != -1)
    lst = []
    while pos != -1:
        pos += 9
        end = value.find("```", pos)
        if end != -1:
            lst.append(value[pos:end])
            pos = value.find("```python", end)
        else:
            pos = -1
    p_check(lst)
    for p in lst:
        programs.append(p)

@predicate(guard=lambda value, programs: isinstance(value, str) and isinstance(programs, list))
def check_structure(value, programs):
    pos = value.find("```javascript")
    p_check(pos != -1)
    lst = []
    while pos != -1:
        pos += 13
        end = value.find("```", pos)
        if end != -1:
            lst.append(value[pos:end])
            pos = value.find("```javascript", end)
        else:
            pos = -1

    p_check(lst)
    for p in lst:
        programs.append(p)

@predicate(guard=lambda value, programs: isinstance(value, str) and isinstance(programs, list))
def check_structure(value, programs):    
    pos = value.find("{")
    end = value.rfind("}")    
    p_check(pos != -1 and end != -1)
    programs.append(value[pos:end+1])

@predicate()
def check_structure(value, programs):
    programs.append("No structure was found in this text.")
    programs.append(value)



# Examples:

valuepython = """
This is a Python code: 
```python 
def multiply(i):
    return i*2

multiply(10)
```
"""

valuejson = """
This is a structure: 
```json 
{"a":[10,20,30],"b":[40,50,60]}
```
"""

programs=[]
check_structure(valuepython, programs)
print(programs[0])

programs=[]
check_structure(valuejson, programs)
print(programs[0])

