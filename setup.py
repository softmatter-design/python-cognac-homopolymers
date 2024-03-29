"""Minimal setup file for tasks project."""

from setuptools import setup, find_packages

setup(
    name='homopolymer-setup',
    version='0.2.6',
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
          'evaluate_homo = chain_evaluation.evaluate_all:evaluate',
          'xpcalc = trajectory.xp_calc:main',
          'modify_udf = polymer_setup.modify:main',
          'sqcalc = chain_evaluation.evaluate_sq:sq'
        ]
    }
)
