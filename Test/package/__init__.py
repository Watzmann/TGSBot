import os

modules = []
for i in os.listdir(__path__[0]):
    if not i.endswith('.py'):
        continue
    m = os.path.splitext(i)[0]
    if not m == '__init__':
        modules.append(m)

__all__ = modules
#print 'all',__all__
