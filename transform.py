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
            child.spelling == "BABEL_SWIFT_WRAPPER_CLASS"):
        mainCursor = next(child.get_children())
        mainCompoundCursor = list(mainCursor.get_children())[1]
        break

print asciitree.draw_tree(
    mainCompoundCursor,
    lambda n: list(n.get_children()),
    lambda n: "%s (%s)" % (n.spelling or n.displayname, str(n.kind)))


TYPE_MAPPING = {
    "int": "Int"
}


def expose(cursor):
    if cursor.kind == CursorKind.UNEXPOSED_EXPR:
        return list(cursor.get_children())[0]
    else:
        return cursor


def transform(cursor):
    if cursor.kind == CursorKind.DECL_STMT:
        varDeclCursor = next(cursor.get_children())
        children = list(varDeclCursor.get_children())

        if len(children) == 1:
            firstChildCursor = expose(children[0])
            if firstChildCursor.kind in (CursorKind.INTEGER_LITERAL, CursorKind.FLOATING_LITERAL):
                literalToken = next(firstChildCursor.get_tokens())
                return "let %s = %s" % (varDeclCursor.spelling, literalToken.spelling)
            elif firstChildCursor.kind == CursorKind.CSTYLE_CAST_EXPR:
                token = list(firstChildCursor.get_tokens())[1]
                unexposedExprCursor = list(firstChildCursor.get_children())[0]
                return "let %s = %s as %s" % (varDeclCursor.spelling, unexposedExprCursor.spelling, TYPE_MAPPING[token.spelling])
            else:
                print firstChildCursor.kind
                return "Not fully implemented: " + str(cursor.kind)
        elif len(children) == 2:
            firstChildCursor = children[0]
            if firstChildCursor.kind == CursorKind.OBJC_CLASS_REF:
                secondChildCursor = expose(children[1])
                if secondChildCursor.spelling == "init":
                    return "let %s: %s = %s()" % (varDeclCursor.spelling, firstChildCursor.spelling, firstChildCursor.spelling)
                else:
                    return "let %s: %s = %s" % (varDeclCursor.spelling, firstChildCursor.spelling, secondChildCursor.spelling)
            else:
                return "Not fully implemented: " + str(cursor.kind)
        else:
            return "Not fully implemented: " + str(cursor.kind)
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
        message = cursor.spelling
        if not message:
            message = list(cursor.get_tokens())[2].spelling
        return "%s.%s()" % (targetCursor.spelling, message)

    return "Not implemented: " + str(cursor.kind)


print ""
for child in mainCompoundCursor.get_children():
    print transform(child)
