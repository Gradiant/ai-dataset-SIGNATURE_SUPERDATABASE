from setuptools import find_packages, setup

version = "0.0.1"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="SIGNATURE_SUPERDATABASE",
    version=version,
    description="SIGNATURE_SUPERDATABASE",
    long_description=long_description,
    url="https://github.com/Gradiant/ai-dataset-SIGNATURE_SUPERDATABASE",
    author="Gradiant",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
)
