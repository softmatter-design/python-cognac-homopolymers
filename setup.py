"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages

setup(
    name='homopolymer-setup',
    version='0.1.0',
    license='proprietary',
    description='Module Experiment',

    author='hsasaki',
    author_email='hsasaki@softmatters.net',
    url='https://github.com/softmatter-design/python-cognac-homopolymers/',

    packages=find_packages(where='src'),
    package_dir={'': 'src'},

    entry_points={
        "console_scripts": [
          'polymer_setup = polymer_setup.setup:main',
          'evaluate_polymer = chain_evaluation.evaluate_all2:evaluate'
        ]
    }
)
