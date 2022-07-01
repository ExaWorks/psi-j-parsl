parsl provider for psi-j-python executors
=========================================

A Parsl `ExecutionProvider` is very similar to a psi-j-python `JobExecutor`.

This package attempts to make `JobExecutor`s usable as Parsl `ExecutionProvider`s.

So far I've tested that the parsl test suite runs to completion without
errors with the local and slurm executors.

Install
=======

The current install is based around the development branches of
various git repositories. To install the stack, do this:

```
git checkout https://github.com/parsl/parsl
cd parsl/
pip install .[psij]
```

This will install parsl, psi/j, and this psi-j-parsl package
from github.
