#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages

long_description = """
"""

if os.path.exists('README.md'):
    long_description = open('README.md').read()

requires = [
    'requests',
    'pyquery',
    'click8',
    'tldextract'
]

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
import cachealot
setup(
    name='cachealot',
    author=cachealot.author,
    version=cachealot.version,
    author_email=cachealot.email,
    description='cachealot is the perfect speedup tool for most web based server applications',
    long_description=long_description,
    license='',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    dependency_links=[],
    url='',
    # scripts=[os.path.join('scripts', s) for s in scripts],
    entry_points='''
    [console_scripts]
    cachealot=cachealot.entrypoints:main
    cachealot-cli=cachealot.entrypoints:interactive
    ''',
    classifiers=[
        'Environment :: Console'
    ]
)
