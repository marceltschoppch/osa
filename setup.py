from setuptools import setup, find_packages
import sys

CLASSIFIERS = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: BSD License
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
    name='Scio',
    version='0.9.1',
    author_email='oss@leapfrogdevelopment.com',
    url='http://bitbucket.org/leapfrogdevelopment/scio/overview',
    description='Scio is a humane SOAP client',
    install_requires=['lxml>=2.2', 'python-dateutil%s' % dateutil_version],
    tests_require=['nose>=1.0', 'Sphinx>=1.0'],
    packages=find_packages(),
    classifiers=CLASSIFIERS,
    )
