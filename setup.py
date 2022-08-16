from setuptools import setup, find_packages

from codecs import open
from os import path
from os import environ
import requests

HERE = path.abspath(path.dirname(__file__))
VERSION = environ.get("VERSION")
DEBUG = True

if not DEBUG:
    pypi_url = "https://pypi.org/pypi/spatial-networks/json"
else:
    pypi_url = "https://test.pypi.org/pypi/spatial-networks/json"

if not VERSION:
    response = requests.get(url=pypi_url)

    latest_version = response.json()["info"]["version"]
    version_numbers = latest_version.split(".")
    VERSION = f"{version_numbers[0]}.{version_numbers[1]}.{int(version_numbers[2]) + 1}"

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
