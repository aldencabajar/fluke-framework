from setuptools import setup

setup(
  name = 'sherpa',
  version = '0.1.0',
  py_modules=['fluke'],
  python_requires= '>=3.8',
  install_requires = ['Click','cookiecutter'],
  entry_points={
    'console_scripts': ['fluke = fluke.cli:main']
  },
)