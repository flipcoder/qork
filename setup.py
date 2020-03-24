#!/usr/bin/python
from __future__ import unicode_literals
from setuptools import setup, find_packages
import sys
if sys.version_info[0]==2:
    sys.exit('Requires python3!')
setup(
    name='qork',
    version='0.1.0',
    description='ModernGL-based python game framework inspired on pygame-zero',
    url='https://github.com/filpcoder/qork',
    author='Grady O\'Connell',
    author_email='flipcoder@gmail.com',
    license='MIT',
    packages=['qork'],
    include_package_data=True,
    install_requires=[
        'moderngl','moderngl-window','numpy','pillow','pyglm','cson'
    ],
    entry_points='''
        [console_scripts]
        qork=qork.zero:main
    ''',
    zip_safe=False
)

