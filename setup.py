from pathlib import Path

from setuptools import setup, find_packages

from flask_dantic import version

here = Path(__file__).resolve().parent
README = (here / "README.md").read_text(encoding="utf-8")
PACKAGE_NAME = "flask-dantic"

setup(
    name=PACKAGE_NAME,
    version=version,
    license="MIT",
    packages=find_packages(exclude=["test"]),
    description=(
        "This package provides a utility to validate pydantic request models "
        "and also serialize db object using pydantic models."
    ),
    long_description=README,
    long_description_content_type="text/markdown",
    author="Vivek Keshore",
    author_email="vivek.keshore@gmail.com",
    url="https://github.com/vivekkeshore/flask-dantic",
    keywords=[
        "sqlalchemy", "alchemy", "mysql", "postgres", "flask",
        "mssql", "sql", "sqlite", "serialize", "pydantic", "validate", "request",
        "orm", "serialization", "performance", "database", "relational"
    ],
    classifiers=[
        # See https://pypi.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
    platforms=["any"],
    python_requires=">=3.6",
)
