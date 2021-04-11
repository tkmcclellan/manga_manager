#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'fuzzywuzzy',
    'bs4',
    'requests',
    'pillow'
]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Tyler Kyle McClellan",
    author_email='the8bitgamer11@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A tool for downloading and reading manga.",
    entry_points={
        'console_scripts': [
            'manga=manga_manager.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords=['manga_manager', 'manga-manager', 'manga', 'manga-scraper', 'manga-reader', 'mangakakalot', 'manga-downloader'],
    name='manga_manager',
    packages=find_packages(include=['manga_manager', 'manga_manager.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/tkmcclellan/manga_manager',
    version='0.1.1',
    zip_safe=False,
)
