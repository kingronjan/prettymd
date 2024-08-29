#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

from os import path

base_dir = path.abspath(path.dirname(__file__))

with open(path.join(base_dir, 'README.md'), encoding='utf8') as readme_file:
    readme = readme_file.read()

requirements = []

setup_requirements = []

test_requirements = []

setup(
    author="kingron",
    author_email='kingronjan@qq.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A tool that formats markdown text in Chinese.",
    install_requires=requirements,
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='prettymd',
    name='prettymd',
    packages=find_packages(include=['prettymd', 'prettymd.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kingronjan/prettymd',
    version='0.1.2',
    zip_safe=False,
)
