#!/usr/bin/env python3

from setuptools import setup

setup(
    name='guidediary',
    description='Diary manipulation tools for Dolphin Guide',
    version='0.1.0',
    author='Anthony Stathers',
    author_email='example@example.org',
    url='https://devnull-as-a-service.com',
    packages=['guidediary'],
    scripts=['bin/mergediaries','bin/extractdiary','bin/reportdiary'],
    install_requires = [
        'python-dateutil',
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
