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


class TestUndefinedIdentifiers(TransformationTestCase):
    def test_var(self):
        self.assertTransformation("i = 623;", "i = 623")

    def test_var_uppercase(self):
        self.assertTransformation("I = 623;", "I = 623")

    def test_class(self):
        self.assertTransformation("obj = [[Object alloc] init];", "obj = Object()")

    def test_class_lowercase(self):
        self.assertTransformation("obj = [[object alloc] init];", "obj = object()")

    def test_property(self):
        self.assertTransformation("babel.swift = transformation.tool;", "babel.swift = transformation.tool")

    def test_chained_property(self):
        self.assertTransformation("babel.swift.language = @\"Python\";", "babel.swift.language = \"Python\"")


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
