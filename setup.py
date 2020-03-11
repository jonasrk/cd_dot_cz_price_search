#!/usr/bin/env python
# flake8: noqa

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = []

setup_requirements = []

test_requirements = []

setup(
    author="Jonas Kemper",
    author_email="jonas.kemper.biz@gmail.com",
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Queries hcd.cz for train ticket prices and emails a summary. AWS Lambda optimized.",
    entry_points={
        "console_scripts": [
            "cd_dot_cz_price_search=cd_dot_cz_price_search.cli:main"
        ]
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="cd_dot_cz_price_search",
    name="cd_dot_cz_price_search",
    packages=find_packages(
        include=["cd_dot_cz_price_search", "cd_dot_cz_price_search.*"]
    ),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/jonasrk/cd_dot_cz_price_search",
    version="0.1.0",
    zip_safe=False,
)
