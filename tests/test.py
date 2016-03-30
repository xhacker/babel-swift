import unittest
from transform import transformCode


class TransformationTestCast(unittest.TestCase):
    def assertSourceCodeEqual(self, a, b):
        a = "\n".join(map(str.strip, a.split("\n"))).strip()
        b = "\n".join(map(str.strip, b.split("\n"))).strip()
        self.assertEqual(a, b)

    def assertTransformation(self, objc, swift):
        self.assertSourceCodeEqual(swift, transformCode(objc))


class TestBuiltinTypes(TransformationTestCast):
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
            "let i = 42\nlet u = i + i * (2 + (3 - 4) + i)")
