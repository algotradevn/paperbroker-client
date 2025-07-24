from setuptools import setup, find_packages

setup(
    name="paperbroker",
    version="0.1",
    packages=find_packages(include=["paperbroker", "paperbroker.*"]),
    install_requires=[],
)
