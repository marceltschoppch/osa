from setuptools import setup, find_packages
import sys

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: LGPL
Natural Language :: English
Programming Language :: Python
Programming Language :: Python :: 2.4
Programming Language :: Python :: 2.5
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Topic :: Software Development :: Object Brokering""".split("\n")

if sys.version_info >= (2, 6):
    dateutil_version = '>=1.4,<2.0'
else:
    dateutil_version = '>=1.4,<1.5'

setup(
    name='osa',
    version='0.1',
    author_email='boz@ipp.mpg.de',
    description='osa is a fast/slim SOAP client.',
    install_requires=['python-dateutil%s' % dateutil_version],
    tests_require=['Sphinx>=1.0'],
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    )
