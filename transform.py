#!/usr/bin/env python

import sys
import re
import os

sys.path.append('/Users/xhacker/Warehouse/llvm/tools/clang/bindings/python')
import clang.cindex
from clang.cindex import CursorKind

import asciitree
from jinja2 import Environment, FileSystemLoader

from oc_structures import OCClass, OCProperty


def generateImplementationFile():
    rawFilepath = sys.argv[1]
    mPath = "input.m"
    env = Environment(loader=FileSystemLoader("./templates"))
    template = env.get_template("method.m")
    with open(rawFilepath) as f, open(mPath, "w") as input:
        input.write(template.render(body=f.read()))
    return mPath


def generateHeaderFile(variableNames, classes):
    hPath = "BabelSwiftHeader.h"
    env = Environment(loader=FileSystemLoader("./templates"))
    template = env.get_template("header.h")
    with open(hPath, "w") as f:
        f.write(template.render(variableNames=variableNames, classes=classes))


def isClassName(identifier):
    return identifier[0].isupper()


def unwrap(cursor):
    """Unwrap cursor.

    For example, @42 in Swift is simply 42.
    """
    if cursor.kind in (CursorKind.IMPLICIT_CAST_EXPR_STMT, CursorKind.OBJC_BOXED_EXPR_STMT):
        return unwrap(list(cursor.get_children())[0])
    else:
        return cursor


BABEL_SWIFT_WRAPPER_CLASS_NAME = "__BABEL_SWIFT_WRAPPER_CLASS__"

TYPE_MAPPING = {
    "int": "Int"
}

CONSTANT_MAPPING = {
    "YES": "true",
    "NO": "false"
}


def transform(cursor, isStmt=False):
    if cursor.kind == CursorKind.DECL_REF_EXPR:
        return cursor.spelling

    elif cursor.kind == CursorKind.IMPLICIT_CAST_EXPR_STMT:
        return transform(unwrap(cursor))

    elif cursor.kind == CursorKind.OBJC_BOXED_EXPR_STMT:
        return transform(unwrap(cursor))

    elif cursor.kind in (CursorKind.INTEGER_LITERAL, CursorKind.FLOATING_LITERAL):
        literalToken = next(cursor.get_tokens())
        return literalToken.spelling

    elif cursor.kind == CursorKind.OBJC_BOOL_LITERAL_EXPR:
        return CONSTANT_MAPPING[cursor.spelling]

    elif cursor.kind == CursorKind.OBJC_SELF_EXPR:
        return cursor.spelling

    elif cursor.kind == CursorKind.OBJC_STRING_LITERAL:
        return cursor.spelling

    elif cursor.kind == CursorKind.OBJC_ARRAY_LITERAL_STMT:
        children = list(cursor.get_children())
        transformedElems = map(transform, children)

        return '[{}]'.format(", ".join(transformedElems))

    elif cursor.kind == CursorKind.CSTYLE_CAST_EXPR:
        targetType = cursor.get_cstyle_cast_target_type()
        valueCursor = unwrap(list(cursor.get_children())[0])
        return "%s as %s\n" % (valueCursor.spelling, TYPE_MAPPING[targetType.spelling])

    elif cursor.kind == CursorKind.DECL_STMT:
        varDeclCursor = next(cursor.get_children())
        children = list(varDeclCursor.get_children())

        if len(children) == 1:
            firstChildCursor = unwrap(children[0])
            return "let %s = %s\n" % (varDeclCursor.spelling, transform(firstChildCursor))
        elif len(children) == 2:
            firstChildCursor = children[0]
            if firstChildCursor.kind == CursorKind.OBJC_CLASS_REF:
                secondChildCursor = unwrap(children[1])
                rhs = transform(secondChildCursor)
                if secondChildCursor.spelling == "init":
                    return "let %s: %s = %s()\n" % (varDeclCursor.spelling, firstChildCursor.spelling, firstChildCursor.spelling)
                else:
                    return "let %s: %s = %s\n" % (varDeclCursor.spelling, firstChildCursor.spelling, rhs)
            else:
                return "// Cursor kind not fully implemented: " + str(cursor.kind) + "\n"
        else:
            return "// Cursor kind not fully implemented: " + str(cursor.kind) + "\n"

    elif cursor.kind == CursorKind.PAREN_EXPR:
        firstChild = list(cursor.get_children())[0]
        return "({})".format(transform(firstChild))

    elif cursor.kind == CursorKind.IF_STMT:
        stmtCursor = list(cursor.get_children())[0]
        bodyCursor = list(cursor.get_children())[1]
        return "if " + transform(stmtCursor) + " " + transform(bodyCursor)

    elif cursor.kind == CursorKind.BINARY_OPERATOR:
        lCursor = list(cursor.get_children())[0]
        rCursor = list(cursor.get_children())[1]
        left = transform(lCursor)
        right = transform(rCursor)
        return "%s %s %s%s" % (left, cursor.spelling, right, "\n" if isStmt else "")

    elif cursor.kind == CursorKind.UNARY_OPERATOR:
        firstToken = list(cursor.get_tokens())[0]
        if firstToken.spelling == "!":
            firstChild = list(cursor.get_children())[0]
            return "!" + transform(firstChild)

        return "// Cursor kind not fully implemented: " + str(cursor.kind) + "\n"

    elif cursor.kind == CursorKind.MEMBER_REF_EXPR:
        member = cursor.spelling
        parent = transform(list(cursor.get_children())[0])
        return "{}.{}".format(parent, member)

    elif cursor.kind == CursorKind.COMPOUND_STMT:
        bodyText = "{\n"
        for child in cursor.get_children():
            bodyText += "   " + transform(child, isStmt=True) + "\n"
        bodyText += "}\n"
        return bodyText

    elif cursor.kind == CursorKind.OBJC_MESSAGE_EXPR:
        targetCursor = unwrap(list(cursor.get_children())[0])
        message = cursor.spelling
        if not message:
            message = list(targetCursor.get_tokens())[1].spelling
        param = ""
        if len(list(cursor.get_children())) > 1:
            paramCursor = list(cursor.get_children())[1]
            param = paramCursor.spelling
        return "%s.%s(%s)\n" % (targetCursor.spelling, message, param)

    return "// Cursor kind not supported: " + str(cursor.kind) + "\n"


def main():
    # clang.cindex.Config.set_library_path("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib")
    clang.cindex.Config.set_library_path("/Users/xhacker/Warehouse/llvm-xcode/Debug/lib")

    # Generate PCH
    pchPath = "tmp/AppKit.pch"
    if not os.path.exists(pchPath):
        print "Generating PCH..."
        index = clang.cindex.Index(clang.cindex.conf.lib.clang_createIndex(True, False))
        appKitHeaderPath = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/System/Library/Frameworks/AppKit.framework/Versions/C/Headers/AppKit.h"
        tu = index.parse(appKitHeaderPath, ["-x", "objective-c-header"])
        tu.save(pchPath)
        print "Done."

    mPath = generateImplementationFile()

    variableNames = []
    classes = {}
    classes[BABEL_SWIFT_WRAPPER_CLASS_NAME] = OCClass(BABEL_SWIFT_WRAPPER_CLASS_NAME)

    for i in xrange(50):
        print "\nIteration %d" % (i,)
        generateHeaderFile(variableNames, classes)

        # clang_createIndex(int excludeDeclarationsFromPCH, int displayDiagnostics);
        index = clang.cindex.Index(clang.cindex.conf.lib.clang_createIndex(True, True))
        tu = index.parse(mPath, [
            "-x", "objective-c",
            "-I/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/usr/include",
            "-include-pch", pchPath])

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

            newClassName = "__BABEL_SWIFT_PSEUDO_CLASS_{}__".format(len(classes))
            newClass = OCClass(newClassName)
            classes[newClassName] = newClass

            property = OCProperty(newClass, identifier)
            classes[className].properties.append(property)
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
                child.spelling == BABEL_SWIFT_WRAPPER_CLASS_NAME):
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
        swiftSource += transform(child, isStmt=True)
    print swiftSource

    with open("output.swift", "w") as f:
        f.write(swiftSource)

if __name__ == "__main__":
    main()
