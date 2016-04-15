#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os

sys.path.append('/Users/xhacker/Warehouse/llvm/tools/clang/bindings/python')
import clang.cindex
from clang.cindex import CursorKind

# clang.cindex.Config.set_library_path("/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib")
clang.cindex.Config.set_library_path("/Users/xhacker/Warehouse/llvm-xcode/Debug/lib")

import asciitree
from jinja2 import Environment, FileSystemLoader

from oc_structures import OCClass, OCVarDecl


def generateImplementationFile(source):
    mPath = "input.m"
    env = Environment(loader=FileSystemLoader("./templates"))
    template = env.get_template("method.m")
    with open(mPath, "w") as input:
        input.write(template.render(body=source))
    return mPath


def generateHeaderFile(varDeclarations, classes):
    hPath = "BabelSwiftHeader.h"
    env = Environment(loader=FileSystemLoader("./templates"))
    template = env.get_template("header.h")
    with open(hPath, "w") as f:
        f.write(template.render(varDeclarations=varDeclarations, classes=classes))


def isClassName(identifier):
    return identifier[0].isupper()


def unwrap(cursor):
    """Unwrap cursor.

    For example, @42 in Swift is simply 42.
    """
    if cursor.kind in (CursorKind.IMPLICIT_CAST_EXPR_STMT, CursorKind.OBJC_BOXED_EXPR_STMT):
        return unwrap(list(cursor.get_children())[0])
    elif cursor.kind == CursorKind.PAREN_EXPR and len(list(cursor.get_children())) == 1:
        return unwrap(list(cursor.get_children())[0])
    else:
        return cursor


BABEL_SWIFT_WRAPPER_CLASS_NAME = "__BABEL_SWIFT_WRAPPER_CLASS__"

TYPE_MAPPING = {
    "int": "Int32"
    ""
}

CONSTANT_MAPPING = {
    "YES": "true",
    "NO": "false"
}


def visit(cursor, isStmt=False):
    if cursor.kind in (CursorKind.DECL_REF_EXPR, CursorKind.OBJC_CLASS_REF):
        return cursor.spelling

    elif cursor.kind == CursorKind.IMPLICIT_CAST_EXPR_STMT:
        return visit(unwrap(cursor))

    elif cursor.kind == CursorKind.OBJC_BOXED_EXPR_STMT:
        return visit(unwrap(cursor))

    elif cursor.kind in (CursorKind.INTEGER_LITERAL, CursorKind.FLOATING_LITERAL):
        try:
            literalToken = next(cursor.get_tokens())
        except StopIteration:
            # If there are no tokens, then it’s probably nil
            return "0"
        return literalToken.spelling

    elif cursor.kind == CursorKind.OBJC_BOOL_LITERAL_EXPR:
        return CONSTANT_MAPPING[cursor.spelling]

    elif cursor.kind == CursorKind.OBJC_SELF_EXPR:
        return cursor.spelling

    elif cursor.kind == CursorKind.OBJC_STRING_LITERAL:
        return cursor.spelling

    elif cursor.kind == CursorKind.OBJC_ARRAY_LITERAL_STMT:
        children = list(cursor.get_children())
        convertedElems = map(visit, children)

        return "[{}]".format(", ".join(convertedElems))

    elif cursor.kind == CursorKind.OBJC_DICTIONARY_LITERAL_STMT:
        it = cursor.get_children()
        dictText = "[\n"
        for child in it:
            key = child
            value = next(it)
            dictText += "    {}: {},\n".format(visit(key), visit(value))
        dictText += "]"
        return dictText

    elif cursor.kind == CursorKind.CSTYLE_CAST_EXPR:
        targetType = cursor.get_cstyle_cast_target_type()
        valueInSwift = visit(unwrap(list(cursor.get_children())[0]))
        if targetType.spelling == "void *" and valueInSwift == "0":
            # nil case
            return "nil"
        elif targetType.spelling in TYPE_MAPPING:
            targetTypeInSwift = TYPE_MAPPING[targetType.spelling]
        else:
            targetTypeInSwift = targetType.spelling
        return "%s as %s\n" % (valueInSwift, targetTypeInSwift)

    elif cursor.kind == CursorKind.DECL_STMT:
        varDeclCursor = next(cursor.get_children())
        children = list(varDeclCursor.get_children())

        if len(children) == 1:
            firstChildCursor = unwrap(children[0])
            return "let %s = %s\n" % (varDeclCursor.spelling, visit(firstChildCursor))
        elif len(children) == 2:
            firstChildCursor = children[0]
            secondChildCursor = unwrap(children[1])
            rhs = visit(secondChildCursor)

            # Since Swift has type inference, drop type (firstChildCursor.spelling) aggressively
            if secondChildCursor.spelling == "init":
                # TODO: this should just use `visit()`
                return "let %s = %s()\n" % (varDeclCursor.spelling, firstChildCursor.spelling)
            else:
                return "let %s = %s\n" % (varDeclCursor.spelling, rhs)
        else:
            return "// Cursor kind not fully implemented: " + str(cursor.kind) + "\n"

    elif cursor.kind == CursorKind.PAREN_EXPR:
        firstChild = list(cursor.get_children())[0]
        return "({})".format(visit(firstChild))

    elif cursor.kind == CursorKind.IF_STMT:
        stmtCursor = list(cursor.get_children())[0]
        bodyCursor = list(cursor.get_children())[1]
        return "if " + visit(stmtCursor) + " " + visit(bodyCursor)

    elif cursor.kind == CursorKind.FOR_STMT:
        bodyCursor = list(cursor.get_children())[3]
        return "for (/* FOR_STMT not fully implemented */) " + visit(bodyCursor)

    elif cursor.kind == CursorKind.WHILE_STMT:
        stmtCursor = list(cursor.get_children())[0]
        bodyCursor = list(cursor.get_children())[1]
        return "while " + visit(stmtCursor) + " " + visit(bodyCursor)

    elif cursor.kind == CursorKind.BINARY_OPERATOR:
        lCursor = list(cursor.get_children())[0]
        rCursor = list(cursor.get_children())[1]
        left = visit(lCursor)
        right = visit(rCursor)
        return "%s %s %s%s" % (left, cursor.spelling, right, "\n" if isStmt else "")

    elif cursor.kind == CursorKind.UNARY_OPERATOR:
        firstToken = list(cursor.get_tokens())[0]
        if firstToken.spelling == "!":
            firstChild = list(cursor.get_children())[0]
            return "!" + visit(firstChild)

        return "// Cursor kind not fully implemented: " + str(cursor.kind) + "\n"

    elif cursor.kind == CursorKind.MEMBER_REF_EXPR:
        member = cursor.spelling
        parent = visit(list(cursor.get_children())[0])
        return "{}.{}".format(parent, member)

    elif cursor.kind == CursorKind.COMPOUND_STMT:
        bodyText = "{\n"
        for child in cursor.get_children():
            bodyText += "   " + visit(child, isStmt=True)
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
            param = visit(paramCursor)

        if message == "alloc" and not param:
            # alloc doesn't need to be called explicitly in Swift
            return visit(targetCursor)

        if message == "init" and not param:
            # Convert to Swift init syntax
            # TODO: support initWithXXX
            return "%s()\n" % (visit(targetCursor))

        return "%s.%s(%s)\n" % (visit(targetCursor), message, param)

    elif cursor.kind == CursorKind.CALL_EXPR:
        it = cursor.get_children()
        callee = next(it)
        callText = visit(callee) + "("

        for child in it:
            callText += visit(child) + ", "

        if callText[-2:] == ", ":
            callText = callText[:-2]

        callText += ")"
        return callText + ("\n" if isStmt else "")

    elif cursor.kind == CursorKind.UNEXPOSED_EXPR:
        # TODO: This is a workaround. All unexposed should be exposed by modifying libclang.
        return visit(list(cursor.get_children())[0])

    return "// Cursor kind not supported: " + str(cursor.kind) + "\n"


def transformCode(objcCode):
    # Generate PCH
    pchPath = "tmp/AppKit.pch"
    if not os.path.exists(pchPath):
        print "Generating PCH..."
        index = clang.cindex.Index(clang.cindex.conf.lib.clang_createIndex(True, False))
        appKitHeaderPath = "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX10.11.sdk/System/Library/Frameworks/AppKit.framework/Versions/C/Headers/AppKit.h"
        tu = index.parse(appKitHeaderPath, ["-x", "objective-c-header"])
        tu.save(pchPath)
        print "Done."

    mPath = generateImplementationFile(objcCode)

    varDeclarations = []
    classes = {}
    classes[BABEL_SWIFT_WRAPPER_CLASS_NAME] = OCClass(BABEL_SWIFT_WRAPPER_CLASS_NAME)
    lastAddedClass = None

    for i in xrange(50):
        print "\nIteration %d" % (i,)
        generateHeaderFile(varDeclarations, classes)

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
        unexpectedInterfaceNamePattern = re.compile("unexpected interface name '(.+)': expected expression")

        if undeclaredIdentifierPattern.match(error):
            m = undeclaredIdentifierPattern.match(error)
            identifier = m.group(1)
            if isClassName(identifier):
                classes[identifier] = OCClass(identifier)
                lastAddedClass = identifier
            else:
                newClassName = "__BABEL_SWIFT_PSEUDO_CLASS_{}__".format(len(classes))
                newClass = OCClass(newClassName)
                classes[newClassName] = newClass

                varDecl = OCVarDecl(newClass, identifier)
                varDeclarations.append(varDecl)
        elif propertyNotFoundPattern.match(error):
            m = propertyNotFoundPattern.match(error)
            identifier = m.group(1)
            className = m.group(2)

            newClassName = "__BABEL_SWIFT_PSEUDO_CLASS_{}__".format(len(classes))
            newClass = OCClass(newClassName)
            classes[newClassName] = newClass

            property = OCVarDecl(newClass, identifier)
            classes[className].properties.append(property)
        elif unexpectedInterfaceNamePattern.match(error):
            # Sometimes variable names are identified as class names
            m = unexpectedInterfaceNamePattern.match(error)
            identifier = m.group(1)
            del classes[identifier]

            newClassName = "__BABEL_SWIFT_PSEUDO_CLASS_{}__".format(len(classes))
            newClass = OCClass(newClassName)
            classes[newClassName] = newClass

            varDecl = OCVarDecl(newClass, identifier)
            varDeclarations.append(varDecl)
        elif "expected identifier" in error:
            # Sometimes variable names are identified as class names
            # E.g. `I = 623;`
            del classes[lastAddedClass]

            newClassName = "__BABEL_SWIFT_PSEUDO_CLASS_{}__".format(len(classes))
            newClass = OCClass(newClassName)
            classes[newClassName] = newClass

            varDecl = OCVarDecl(newClass, lastAddedClass)
            varDeclarations.append(varDecl)
        else:
            break
    if len(errors) > 0:
        print "Syntax error."
        return

    generateHeaderFile(varDeclarations, classes)

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

    swiftSource = ""
    for child in mainCompoundCursor.get_children():
        swiftSource += visit(child, isStmt=True)
    return swiftSource


if __name__ == "__main__":
    filepath = sys.argv[1]
    with open(filepath, "r") as f:
        source = f.read()
    swiftCode = transformCode(source)
    print swiftCode

    if swiftCode:
        with open("output.swift", "w") as f:
            f.write(swiftCode)
