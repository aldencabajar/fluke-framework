"""setup for fluke-framework package"""
from setuptools import setup

setup(
  name = 'fluke',
  version = '0.1.0',
  py_modules=['fluke'],
  python_requires= '>=3.8',
  install_requires = ['Click','cookiecutter', 'pyyaml'],
  entry_points={
    'console_scripts': ['fluke = fluke.cli:main']
  },
)
