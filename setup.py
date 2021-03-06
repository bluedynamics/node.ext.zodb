from setuptools import setup
from setuptools import find_packages
import codecs
import os


def read_file(name):
    with codecs.open(
        os.path.join(os.path.dirname(__file__), name),
        encoding='utf-8'
    ) as f:
        return f.read()


version = '1.4.dev0'
shortdesc = 'Node Implementation with ZODB persistence'
longdesc = '\n\n'.join([read_file(name) for name in [
    'README.rst',
    'CHANGES.rst',
    'LICENSE.rst'
]])


setup(
    name='node.ext.zodb',
    version=version,
    description=shortdesc,
    long_description=longdesc,
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='node odict zodb persistent tree',
    author='BlueDynamics Alliance',
    author_email='dev@bluedynamics.com',
    url='',
    license='BSD',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['node', 'node.ext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'node',
        'ZODB3'
    ],
    test_suite='odict.tests'
)
