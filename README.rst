=============
manga_manager
=============


.. image:: https://img.shields.io/pypi/v/manga_manager.svg
        :target: https://pypi.python.org/pypi/manga_manager

.. image:: https://readthedocs.org/projects/manga-manager/badge/?version=latest
        :target: https://manga-manager.readthedocs.io/en/latest/?version=latest
        :alt: Documentation Status




Tired of reading manga on online manga sites?
Tired of losing track of which chapter you were reading?
Ever wish you could download chapters to a PDF?
Looking for a better solution?

Me too! That's why this tool exists.

Heavily inspired by anime-downloader_.

.. _anime-downloader: https://github.com/anime-dl/anime-downloader

* Free software: MIT license
* Documentation: https://manga-manager.readthedocs.io.


Features
--------

* Download and read any manga.
* Track reading progress.
* Search and download.

Supported Operating Systems
---------------------------

* Windows
* Mac OS
* Linux

Supported Sites
---------------

* Mangakakalot

Installation
------------

Using pip:

.. code-block:: console

        $ python -m pip install manga_manager

`Full instructions`_

.. _Full instructions: https://manga-manager.readthedocs.io/en/latest/installation.html

Usage
-----

manga_manager has four (4) commands, ``add``, ``remove``, ``edit``, and ``read``. To get started with reading
a manga, enter the commands:

.. code-block:: console

        $ manga add attack on titan
        $ manga read attack on titan

As of writing this README, manga_manager is not fully configured to be used as a library, but it will be soon.

A full description of the usage of manga_manager can be found here_.

.. _here: https://manga-manager.readthedocs.io/en/latest/usage.html

Credits
-------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

Footnote
--------
`Please bear in mind the production of this repo is for educational/research purposes only with regards to webscraping and PDF conversion of manga, we take no responsibility for people who decide to actually use this repository.`