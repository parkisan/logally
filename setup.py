#!/usr/bin/env python
from setuptools import setup

setup(
  name='LogAlly',
  version='0.1.1',
  packages=["tests", "tests.plugins", "tests.plugins.tables",
            "tests.plugins.datasources", "tests.lib", "logally",
            "logally.plugins", "logally.plugins.tables",
            "logally.plugins.datasources", "logally.lib", "logally.qt"],
  url='http://code.google.com/p/logally/',
  license='Apache License 2.0',
  author='Jordi Sanchez',
  author_email='parki.san@gmail.com',
  description='Tool and module to help analyze event-based data.',
  test_suite="tests",
  scripts=["scripts/runlogally.py"],
  install_requires=["python_datetime_tz"]
)
