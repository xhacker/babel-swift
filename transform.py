#!/usr/bin/env python

import sys
import re
import clang.cindex
from clang.cindex import CursorKind
import asciitree
from jinja2 import Environment, FileSystemLoader

from oc_class import OCClass


def wrapImplementationFile():
    rawFilepath = sys.argv[1]
    mPath = "input.m"
    env = Environment(loader=FileSystemLoader("./templates"))
    template = env.get_template("method.m")
    with open(rawFilepath) as f, open(mPath, "w") as input:
        input.write(template.render(body=f.read()))
    return mPath


def generateHeaderFile(variableNames, classes):
    hPath = "BabelSwiftIdentifiers.h"
    env = Environment(loader=FileSystemLoader("./templates"))
    template = env.get_template("header.h")
    with open(hPath, "w") as f:
        f.write(template.render(variableNames=variableNames, classes=classes))


def isClassName(identifier):
    return identifier[0].isupper()


def expose(cursor):
    if cursor.kind == CursorKind.UNEXPOSED_EXPR:
        return list(cursor.get_children())[0]
    else:
        return cursor


TYPE_MAPPING = {
    "int": "Int"
}


def transform(cursor):
    if cursor.kind == CursorKind.DECL_REF_EXPR:
        return cursor.spelling

    elif cursor.kind == CursorKind.DECL_STMT:
        varDeclCursor = next(cursor.get_children())
        children = list(varDeclCursor.get_children())

        if len(children) == 1:
            firstChildCursor = expose(children[0])
            if firstChildCursor.kind in (CursorKind.INTEGER_LITERAL, CursorKind.FLOATING_LITERAL):
                literalToken = next(firstChildCursor.get_tokens())
                return "let %s = %s\n" % (varDeclCursor.spelling, literalToken.spelling)
            elif firstChildCursor.kind == CursorKind.CSTYLE_CAST_EXPR:
                token = list(firstChildCursor.get_tokens())[1]
                unexposedExprCursor = list(firstChildCursor.get_children())[0]
                return "let %s = %s as %s\n" % (varDeclCursor.spelling, unexposedExprCursor.spelling, TYPE_MAPPING[token.spelling])
            else:
                print firstChildCursor.kind
                return "Not fully implemented: " + str(cursor.kind)
        elif len(children) == 2:
            firstChildCursor = children[0]
            if firstChildCursor.kind == CursorKind.OBJC_CLASS_REF:
                secondChildCursor = expose(children[1])
                rhs = transform(secondChildCursor)
                if secondChildCursor.spelling == "init":
                    return "let %s: %s = %s()\n" % (varDeclCursor.spelling, firstChildCursor.spelling, firstChildCursor.spelling)
                else:
                    return "let %s: %s = %s\n" % (varDeclCursor.spelling, firstChildCursor.spelling, rhs)
            else:
                return "// Not fully implemented: " + str(cursor.kind) + "\n"
        else:
            return "// Not fully implemented: " + str(cursor.kind) + "\n"

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
        bodyText += "}\n"
        return bodyText

    elif cursor.kind == CursorKind.OBJC_MESSAGE_EXPR:
        targetCursor = list(cursor.get_children())[0]
        message = cursor.spelling
        if not message:
            message = list(targetCursor.get_tokens())[1].spelling
        param = ""
        if len(list(cursor.get_children())) > 1:
            paramCursor = list(cursor.get_children())[1]
            param = paramCursor.spelling
        return "%s.%s(%s)\n" % (targetCursor.spelling, message, param)

    return "// Not implemented: " + str(cursor.kind) + "\n"


def main():
    clang.cindex.Config.set_library_path("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib")

    mPath = wrapImplementationFile()

    variableNames = []
    classes = {}

    for i in xrange(50):
        print "\nIteration %d" % (i,)
        generateHeaderFile(variableNames, classes)

        index = clang.cindex.Index(clang.cindex.conf.lib.clang_createIndex(False, True))
        tu = index.parse(mPath, ["-x", "objective-c", "-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/usr/include"])

        errors = filter(lambda d: d.severity >= 3, tu.diagnostics)
        if len(errors) == 0:
            break

        first = errors[0]
        error = first.spelling

        undeclaredIdentifierPattern = re.compile("use of undeclared identifier '(.+)'")
        propertyNotFoundPattern = re.compile("property '(.+)' not found on object of type '(.+) \\*'")

        if undeclaredIdentifierPattern.match(error):
            m = undeclaredIdentifierPattern.match(error)
            identifier = m.group(1)
            if isClassName(identifier):
                classes[identifier] = OCClass(identifier)
            else:
                variableNames.append(identifier)
        elif propertyNotFoundPattern.match(error):
            m = propertyNotFoundPattern.match(error)
            identifier = m.group(1)
            className = m.group(2)
            classes[className].properties.append(identifier)
        else:
            break
    if len(errors) > 0:
        print "Syntax error."
        return

    generateHeaderFile(variableNames, classes)

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

    print ""
    swiftSource = ""
    for child in mainCompoundCursor.get_children():
        swiftSource += transform(child)
    print swiftSource

    with open("output.swift", "w") as f:
        f.write(swiftSource)

if __name__ == "__main__":
    main()
