from setuptools import setup, find_packages

setup(
    name="searchtok",
    version="2.0",
    packages=find_packages(),
    author='Keenan Chen',
    author_email="cyt.keenan@gmail.com",
    install_requires=
        [
        'requests'
    ],
    py_modules=['search'],

    )