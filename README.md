# GEDCOM Project for CS-555 (Agile Development)

## Description
This project served as practice for integrating some of the Extreme Programming (XP) and Scrum methods on a small team project. It is a simple command-line program, analogous to lint and PyLint, to discover errors and anomalies in GEDCOM genealogy files. 

The project was implemented with Python and spanned across 15 weeks totalling 4 coding sprints consisting of 8 user stories (2 per developer) over an average of 2 weeks. Additionally, with a `.env` file, there is a database functionality with MongoDB to store all the entires of the families and individuals (refer to `.env_example` for a sample `.env` file).

## Installation
Use the package manager pip to install all the packages found in requirements.txt
```bash
pip install -r requirements.txt
```

## Usage

To run the parser:
```bash
python3 gedcomParser.py
```

To run the unit tests:
```bash
python3 unit_testing.py
```

## Authors
* Eric Altenburg
* Megha Mansuria
* Cassidy Savettiere
* Sarah Wiessler
