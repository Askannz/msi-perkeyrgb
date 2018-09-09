#!/usr/bin/env python
from os.path import dirname, join
from setuptools import setup


setup(
    name='msi-perkeyrgb',
    version='1.0',
    description='Configuration tool for per-key RGB keyboards on MSI laptops.',
    long_description=open(
        join(dirname(__file__), 'README.md')).read(),
    url='https://github.com/Askannz/msi-perkeyrgb',
    author='Robin Lange',
    author_email='robin.langenc@gmail.com',
    license='MIT',
    py_modules=['msi-perkeyrgb'],
    entry_points={
        'console_scripts': [
            'msi-perkeyrgb=msi-perkeyrgb:main',
        ],
    },
    keywords=['msi', 'rgb', 'keyboard', 'per-key'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
