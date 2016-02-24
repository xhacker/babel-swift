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

for child in cursor.get_children():
    if (child.kind == CursorKind.OBJC_IMPLEMENTATION_DECL and
            child.spelling == "BABEL_SWIFT_WRAPPER"):
        mainCursor = next(child.get_children())
        mainCompoundCursor = list(mainCursor.get_children())[1]
        break

print asciitree.draw_tree(
    mainCompoundCursor,
    lambda n: list(n.get_children()),
    lambda n: "%s (%s)" % (n.spelling or n.displayname, str(n.kind)))


def transform(cursor):
    if cursor.kind == CursorKind.DECL_STMT:
        varDeclCursor = next(cursor.get_children())
        children = list(varDeclCursor.get_children())

        if len(children) == 1:
            literalCursor = children[0]
            literalToken = next(literalCursor.get_tokens())
            return "let %s = %s" % (varDeclCursor.spelling, literalToken.spelling)
        else:
            typeCursor = children[0]
            return "let %s: %s = %s" % (varDeclCursor.spelling, typeCursor.spelling, "nil")
    elif cursor.kind == CursorKind.IF_STMT:
        stmtCursor = list(cursor.get_children())[0]
        bodyCursor = list(cursor.get_children())[1]
        return "if " + transform(stmtCursor) + " " + transform(bodyCursor)
    elif cursor.kind == CursorKind.BINARY_OPERATOR:
        token = list(cursor.get_tokens())[1]
        lCursor = list(cursor.get_children())[0]
        rCursor = list(cursor.get_children())[1]
        lToken = next(lCursor.get_tokens())
        rToken = next(rCursor.get_tokens())
        return "%s %s %s" % (lToken.spelling, token.spelling, rToken.spelling)
    elif cursor.kind == CursorKind.COMPOUND_STMT:
        bodyText = "{\n"
        for child in cursor.get_children():
            bodyText += "   " + transform(child) + "\n"
        bodyText += "}"
        return bodyText
    elif cursor.kind == CursorKind.OBJC_MESSAGE_EXPR:
        targetCursor = next(cursor.get_children())
        return "%s.%s()" % (targetCursor.spelling, cursor.spelling)

    return str(cursor.kind)


print ""
for child in mainCompoundCursor.get_children():
    print transform(child)
