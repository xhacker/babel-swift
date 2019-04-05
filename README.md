# Babel Swift

An Objective-C to Swift converter. This is my CMPT 497 course project at SFU. Final report can be found [here](https://github.com/xhacker/babel-swift-report/blob/master/report.pdf).

## Useful Commands

Dump AST using Clang:

```bash
clang -Xclang -ast-dump -fsyntax-only input.m
```

## Test

Install [forked version of Clang](https://github.com/xhacker/clang).

```sh
python2.7 -m pytest -v tests/test.py
```
