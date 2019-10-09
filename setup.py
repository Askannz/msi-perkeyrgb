#!/usr/bin/env python
from os.path import dirname, join
from setuptools import setup


setup(
    name='msi-perkeyrgb',
    version='1.4-effect-alpha',
    description='Configuration tool for per-key RGB keyboards on MSI laptops.',
    long_description=open(
        join(dirname(__file__), 'README.md')).read(),
    url='https://github.com/Askannz/msi-perkeyrgb',
    author='Robin Lange',
    author_email='robin.langenc@gmail.com',
    license='MIT',
    packages=['msi_perkeyrgb'],
    entry_points={
        'console_scripts': [
            'msi-perkeyrgb=msi_perkeyrgb.main:main',
        ],
    },
    package_data={'msi_perkeyrgb': ['presets/*.json']},
    keywords=['msi', 'rgb', 'keyboard', 'per-key'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
