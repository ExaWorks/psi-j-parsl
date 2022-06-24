from setuptools import setup

with open('requirements.txt') as f:
    install_requires = f.readlines()

setup(name='psi-j-parsl',
      version='0.2021113001',
      description='parsl / psi-j integration',
      url='http://github.com/ExaWorks/psi-j-parsl',
      author='exaworks',
      author_email='benc@hawaga.org.uk',
      license='unknown',
      packages=['pppj'],
      zip_safe=False,
      install_requires=install_requires)

