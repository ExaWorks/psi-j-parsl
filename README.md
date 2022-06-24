parsl provider for psi-j-python executors
=========================================

A Parsl `ExecutionProvider` is very similar to a psi-j-python `JobExecutor`.

This package attempts to make `JobExecutor`s usable as Parsl `ExecutionProvider`s.

So far I've tested that the parsl test suite runs to completion without
errors with the local and slurm executors.

Usage
=====

(.... means get a checkout of the relevant repo)

``
cd ..../src/psi-j-parsl
pip install .
``

then install psi-j-python - this is a bit messy

and then install parsl:

``
cd ..../src/parsl
pip install -e .
pip install -r ./test-requirements.txt 

pytest parsl/tests/ --config ..../src/psi-j-parsl/parsl_config.py -k "not cleannet"
``
