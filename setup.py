from setuptools import setup, find_packages

setup(name='isisdm', version='0.0.0',
      install_requires=['deform', 'colander'],
      packages=find_packages(),
    )