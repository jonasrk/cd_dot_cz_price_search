https://docs.aws.amazon.com/lambda/latest/dg/python-package.html

test

```
Create a ZIP archive with the contents of the library.

zip -r9 ${OLDPWD}/function.zip .

Add your function code to the archive.

zip -g function.zip lambda_function.py

```

======================
cd-dot-cz-price-search
======================

.. image:: https://img.shields.io/pypi/v/cd_dot_cz_price_search.svg
:target: https://pypi.python.org/pypi/cd_dot_cz_price_search

.. image:: https://img.shields.io/travis/jonasrk/cd_dot_cz_price_search.svg
:target: https://travis-ci.com/jonasrk/cd_dot_cz_price_search

.. image:: https://readthedocs.org/projects/cd-dot-cz-price-search/badge/?version=latest
:target: https://cd-dot-cz-price-search.readthedocs.io/en/latest/?badge=latest
:alt: Documentation Status

Queries cd.cz for train ticket prices and emails a summary. AWS Lambda optimized.

-   Free software: MIT license
-   Documentation: https://cd-dot-cz-price-search.readthedocs.io.

## Features

-   TODO

## Credits

This package was created with Cookiecutter* and the `audreyr/cookiecutter-pypackage`* project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
