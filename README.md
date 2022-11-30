## Swirl - An S1S Model Checker

### Overview

Swirl is a model checker for S1S, the monadic second-order logic of one successor. An example formula in S1S is as follows:

> $\forall S . \exists y .\forall x . y \in S \land x \in S \land y \le x$

In plain English, this says: for all sets S, there is a y in S such that y is less than or equal to x, for all elements x in S. In Swirl, we can write this as follows: 

> forall S . exists y . forall x . y in S & x in S & y <= S

### Installation

#### Prerequisites
- Python 3.10
- [Lark](https://lark-parser.readthedocs.io/en/latest/#)
- [Spot](https://spot.lre.epita.fr/)


Once these are installed,  `python test/test.py` can be used to run the test suite, verifying the tool's installation.

### Usage

In this repository, `main.py` is Swirl's primary script. This can be run directly, interactively prompting the user for a formula to check. 

Alternatively, the `-f` flag can be passed alongside a file name in order to make Swirl read the formula from a file. `-h` provides some helpful information on Swirl's arguments.

For some examples of formulas in Swirl's grammar, see the `examples` folder. `lib/grammar.py` contains the full grammar, for further reference.

### Licensing and Copyright Information

This project is distributed under GNU GPL 3, as a core dependency, Spot, is also licensed in this manner. See COPYING.txt for details.

Copyright (C) 2022 Christian Fontenot