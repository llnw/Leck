#!/usr/bin/python

from distutils.core import setup
import os

setup( name='leck',
       version='1.0.0',
       description='Gerrit like and per-branch review for GitHub pull requests',
       author='Chris Christensen',
       author_email='cchristensen@llnw.com',
       url='llnw/Leck',
       packages=['Leck', 'Leck.external']
)
