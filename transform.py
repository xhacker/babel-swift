#!/usr/bin/env python

import clang.cindex
import asciitree

clang.cindex.Config.set_library_path("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib")

# index = clang.cindex.Index.create()
index = clang.cindex.Index(clang.cindex.conf.lib.clang_createIndex(False, True))
tu = index.parse("test.m", ["-x", "objective-c"])

cursor = tu.cursor
print cursor.spelling

print asciitree.draw_tree(
    tu.cursor,
    lambda n: list(n.get_children()),
    lambda n: "%s (%s)" % (n.spelling or n.displayname, str(n.kind).split(".")[1]))
