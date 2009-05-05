
from distutils.core import setup
setup(name='mym',
      version='1.0',
      packages=['Mypackage'],
      package_data={'Mypackage':['data/*.dat']},
      scripts=['modules.py',])
