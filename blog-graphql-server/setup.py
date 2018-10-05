# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

from jetblack.blog import __version__ as version

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Load the requirements from the text file.
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [x.strip() for x in f.readlines() if x.strip()]

setup(
    name='blog_graphql_server',
    version=version,
    description='A graphqll blog',
    long_description=long_description,
    url='https://github.com/rob-blackbourn/scratch-python/blog-graphql-server',
    author='Rob Blackbourn',
    author_email='rob.blackbourn@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Framework :: AsyncIO',
    ],
    keywords='blog',
    scripts=['bin/start'],
    packages=find_packages(exclude=['tests', 'examples']),
    install_requires=requirements,
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'pytest-asyncio']
)
