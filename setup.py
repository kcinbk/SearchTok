from setuptools import setup, find_packages

setup(
    name="SearchTok",
    version="1.0",
    packages=find_packages(),
    author='Keenan Chen',
    install_requires=[
        'requests',
        'json',
        'time'
                     ]
    )