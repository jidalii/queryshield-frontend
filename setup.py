from setuptools import setup, find_packages

def read_requirements(filename):
    with open(filename, "r") as file:
        return file.read().splitlines()

setup(
    name="queryshield",
    version="0.1",
    packages=find_packages(),
    install_requires=read_requirements("requirements.txt"),  # Include your project's dependencies here
    include_package_data=True,
)
