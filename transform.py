#!/usr/bin/env python

import sys
import clang.cindex
from clang.cindex import CursorKind
import asciitree

clang.cindex.Config.set_library_path("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib")

# index = clang.cindex.Index.create()
index = clang.cindex.Index(clang.cindex.conf.lib.clang_createIndex(False, True))
tu = index.parse(sys.argv[1], ["-x", "objective-c", "-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/usr/include"])

cursor = tu.cursor
print cursor.spelling
print ""

# cursorForMain = None
for child in cursor.get_children():
    if child.spelling == "main":
        mainCompoundCursor = next(child.get_children())
        break

print asciitree.draw_tree(
    mainCompoundCursor,
    lambda n: list(n.get_children()),
    lambda n: "%s (%s)" % (n.spelling or n.displayname, str(n.kind)))


def transform(cursor):
    if cursor.kind == CursorKind.DECL_STMT:
        varDeclCursor = next(child.get_children())
        literalCursor = next(varDeclCursor.get_children())
        literalToken = next(literalCursor.get_tokens())
        return "let %s = %s" % (varDeclCursor.spelling, literalToken.spelling)


print ""
for child in mainCompoundCursor.get_children():
    print transform(child)
