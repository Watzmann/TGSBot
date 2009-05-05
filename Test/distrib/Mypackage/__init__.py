"""Construktor for Mypackage

Interesting detail is the way the variable '__all__' is constructed.
"""
import os

not_module = ['__init__.py',]
def module(m):
    return m not in not_module

#print type(__path__), __path__
os.chdir(__path__[0])
##for i in os.listdir('.'):
##    if i.endswith('.py'):
##        print i

files = filter(module,[i for i in os.listdir('.') if i.endswith('.py')])
modules = []
for m in files:
    modules.append(os.path.splitext(m)[0])
    
print modules

__all__ = modules

comment1 = """  Now we import the submodules.
  Only this gives knowledge of test'x' to Mypackage."""
import test1
import test2
