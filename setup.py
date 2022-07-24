from setuptools import setup, find_packages

from codecs import open
from os import path
from os import environ

HERE = path.abspath(path.dirname(__file__))
VERSION = environ.get("VERSION", "0.0.1")
if not VERSION:
    VERSION = "0.0.1"
    os.environ["VERSION"] = VERSION

print(f"VERSION: {VERSION}")


with open(path.join(HERE, "README.md"), encoding="utf-8") as f:
    long_description = f.read()


with open(path.join(HERE, "requirements.txt"), encoding="utf-8") as f:
    requirements = f.read().split("\n")


setup(
    name="spatial-networks",
    version=VERSION,
    description="Demo library on Spatial Networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pauldechorgnat/spatial-networks",
    author="Paul Déchorgnat",
    author_email="dev.dechorgnp@gmail.com",
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
    packages=["spatial_networks"],
    include_package_data=True,
    install_requires=requirements,
)
