# Babel Swift

Something.

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
