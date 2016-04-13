import unittest
from transform import transformCode


class TransformationTestCase(unittest.TestCase):
    def assertSourceCodeEqual(self, a, b):
        a = "\n".join(map(str.strip, a.split("\n"))).strip()
        b = "\n".join(map(str.strip, b.split("\n"))).strip()
        self.assertEqual(a, b)

    def assertTransformation(self, objc, swift):
        self.assertSourceCodeEqual(swift, transformCode(objc))


class TestBuiltinTypes(TransformationTestCase):
    def test_int(self):
        self.assertTransformation("NSInteger i = 42;", "let i = 42")
        self.assertTransformation("int i = 42;", "let i = 42")

    def test_float(self):
        self.assertTransformation("double e = 2.71828;", "let e = 2.71828")
        self.assertTransformation("float e = 2.71828;", "let e = 2.71828")
        self.assertTransformation("CGFloat e = 2.71828;", "let e = 2.71828")

    def test_arithmetic(self):
        self.assertTransformation(
            """
            NSInteger i = 42;
            NSUInteger u = i + i * (2 + (3 - 4) + i);
            """,
            """
            let i = 42
            let u = i + i * (2 + (3 - 4) + i)
            """)

    def test_cstyle_cast(self):
        self.assertTransformation("float i = (float) 42;", "let i = 42 as float")

    def test_nsarray(self):
        self.assertTransformation("arr = @[@1, @\"abc\", someObj];", "arr = [1, \"abc\", someObj]")

    def test_nsdictionary(self):
        self.assertTransformation(
            """
            NSDictionary *dict = @{
                kPADCurrentPrice: @19.99,
                kPADDevName: @"Regular SIA",
                kPADProductName: @"Inboard",
            };
            """,
            """
            let dict = [
                kPADCurrentPrice: 19.99,
                kPADDevName: "Regular SIA",
                kPADProductName: "Inboard",
            ]
            """)

    def test_boxed_expr(self):
        self.assertTransformation("num = @(600 + 23);", "num = 600 + 23")


class TestUndefinedIdentifiers(TransformationTestCase):
    def test_var(self):
        self.assertTransformation("i = 623;", "i = 623")

    def test_var_uppercase(self):
        self.assertTransformation("I = 623;", "I = 623")

    def test_class(self):
        self.assertTransformation("Object *obj = obj0;", "let obj = obj0")

    def test_class_lowercase(self):
        self.assertTransformation("object *obj = obj0;", "let obj = obj0")

    def test_property(self):
        self.assertTransformation("babel.swift = transformation.tool;", "babel.swift = transformation.tool")

    def test_chained_property(self):
        self.assertTransformation("babel.swift.language = @\"Python\";", "babel.swift.language = \"Python\"")

    def test_chained_property_self(self):
        self.assertTransformation("self.babel.swift = @\"Awesome\";", "self.babel.swift = \"Awesome\"")


class TestConditional(TransformationTestCase):
    def test_if(self):
        objc = """
        if (answer == 42) {
            answer += 1;
        }
        """
        swift = """
        if answer == 42 {
            answer += 1
        }
        """
        self.assertTransformation(objc, swift)

    def test_for(self):
        objc = """
        for (int i = 0; i < 10; ++i) {
            NSLog(@\"%d\n\", i);
        }
        """
        swift = """
        for i in 0..<10 {
            NSLog(\"%d\n\", i)
        }
        """
        self.assertTransformation(objc, swift)

    def test_while(self):
        objc = """
        while (YES) {
            NSLog(@\"NO\");
        }
        """
        swift = """
        while true {
            NSLog(\"NO\")
        }
        """
        self.assertTransformation(objc, swift)


class TestMessage(TransformationTestCase):
    def test_simple(self):
        self.assertTransformation("[popover run];", "popover.run()")

    def test_one_arg(self):
        self.assertTransformation(
            "[currentInstallation setDeviceTokenFromData:deviceToken];",
            "currentInstallation.setDeviceTokenFromData(deviceToken)")

    def test_multi_args(self):
        self.assertTransformation(
            "[[RMSharedUserDefaults standardUserDefaults] setValue:token forKey:INUserDefaultsDribbbleToken];",
            "RMSharedUserDefaults.standardUserDefaults().setValue(token, forKey:INUserDefaultsDribbbleToken)")

    def test_alloc_init(self):
        self.assertTransformation(
            "NSPopover *popover = [[NSPopover alloc] init];",
            "let popover = NSPopover()")

    def test_init_by_class_method(self):
        self.assertTransformation(
            "NSMutableArray *arr = [NSMutableArray array];",
            "let arr = NSMutableArray()")

    def test_selector(self):
        self.assertTransformation(
            "menuItem.action = @selector(eventMenuItemClicked:);",
            "menuItem.action = #selector(eventMenuItemClicked(_:))")


class TestFunctionCall(TransformationTestCase):
    def test_simple(self):
        self.assertTransformation("CGRectMake(0, 0, 233, 233);", "CGRectMake(0, 0, 233, 233)")

    def test_undefined(self):
        self.assertTransformation("call_function(some, argument);", "call_function(some, argument)")

    def test_nslog(self):
        self.assertTransformation("NSLog(@\"Oh %@ %@\", a, b);", "NSLog(\"Oh %@ %@\", a, b)")


class TestSwiftSpecialSyntax(TransformationTestCase):
    def test_enum(self):
        self.assertFalse(
            "style = UITableViewCellStyleDefault;",
            "style = .Default")

    def test_let(self):
        self.assertTransformation("int a = 1;", "let a = 1")

    def test_var(self):
        self.assertTransformation("int a = 1; a = 2;", "var a = 1\na = 2")
